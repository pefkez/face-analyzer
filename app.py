import os, uuid, time, threading, sqlite3, json, datetime
from pathlib import Path
from collections import defaultdict
from flask import Flask, render_template, request, jsonify, send_from_directory, g
from analyzer import analyze_face

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['HISTORY_FOLDER'] = 'history'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['CLEANUP_MAX_AGE'] = 3600
app.config['DATABASE'] = 'face_analyzer.db'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

RATE_LIMIT = 10
RATE_WINDOW = 60
_rate_store = defaultdict(list)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['HISTORY_FOLDER'], exist_ok=True)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                total_severity INTEGER,
                problems_count INTEGER,
                tier_id TEXT,
                tier_label TEXT,
                image_path TEXT,
                result_json TEXT
            );
            CREATE TABLE IF NOT EXISTS before_after (
                id TEXT PRIMARY KEY,
                before_id TEXT NOT NULL,
                after_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                improvement INTEGER,
                FOREIGN KEY(before_id) REFERENCES analyses(id),
                FOREIGN KEY(after_id) REFERENCES analyses(id)
            );
        """)
        db.commit()


@app.teardown_appcontext
def close_db(_e):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_rate_limited(ip):
    now = time.time()
    window_start = now - RATE_WINDOW
    _rate_store[ip] = [t for t in _rate_store[ip] if t > window_start]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        return True
    _rate_store[ip].append(now)
    return False


def cleanup_old_files():
    while True:
        time.sleep(600)
        now = time.time()
        for f in Path(app.config['UPLOAD_FOLDER']).iterdir():
            if f.is_file() and now - f.stat().st_mtime > app.config['CLEANUP_MAX_AGE']:
                f.unlink(missing_ok=True)
        for f in Path(app.config['HISTORY_FOLDER']).iterdir():
            if f.is_file() and now - f.stat().st_mtime > 86400 * 7:
                f.unlink(missing_ok=True)


cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/history')
def history_page():
    return render_template('history.html')


@app.route('/compare')
def compare_page():
    return render_template('compare.html')


@app.route('/api/history')
def get_history():
    db = get_db()
    rows = db.execute(
        'SELECT id, timestamp, total_severity, problems_count, tier_label FROM analyses ORDER BY timestamp DESC LIMIT 50'
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/history/<analysis_id>')
def get_analysis(analysis_id):
    db = get_db()
    row = db.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,)).fetchone()
    if not row:
        return jsonify({"error": "Not found"}), 404
    result = dict(row)
    result['result'] = json.loads(result.pop('result_json'))
    return jsonify(result)


@app.route('/api/history/<analysis_id>', methods=['DELETE'])
def delete_analysis(analysis_id):
    db = get_db()
    row = db.execute('SELECT image_path FROM analyses WHERE id = ?', (analysis_id,)).fetchone()
    if row:
        img_path = row['image_path']
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except OSError:
                pass
        db.execute('DELETE FROM analyses WHERE id = ?', (analysis_id,))
        db.execute('DELETE FROM before_after WHERE before_id = ? OR after_id = ?', (analysis_id, analysis_id))
        db.commit()
    return jsonify({"ok": True})


@app.route('/api/before-after')
def get_before_after():
    db = get_db()
    rows = db.execute('''
        SELECT ba.*, b.total_severity as before_severity, b.tier_label as before_tier,
               a.total_severity as after_severity, a.tier_label as after_tier
        FROM before_after ba
        JOIN analyses b ON ba.before_id = b.id
        JOIN analyses a ON ba.after_id = a.id
        ORDER BY ba.timestamp DESC LIMIT 20
    ''').fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/analyze', methods=['POST'])
def analyze():
    ip = request.remote_addr or 'unknown'
    if is_rate_limited(ip):
        return jsonify({"error": "Слишком много запросов. Подождите минуту."}), 429

    if 'photo' not in request.files:
        return jsonify({"error": "Файл не загружен"}), 400

    file = request.files['photo']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Неверный формат. Допустимы: PNG, JPG, JPEG, WEBP"}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    compare_with = request.form.get('compare_with')

    try:
        result = analyze_face(filepath)
    except Exception:
        os.remove(filepath)
        return jsonify({"error": "Внутренняя ошибка сервера."}), 500

    if "error" in result:
        os.remove(filepath)
        return jsonify(result), 400

    result["image_url"] = f"/uploads/{filename}"

    analysis_id = uuid.uuid4().hex
    db = get_db()
    db.execute(
        'INSERT INTO analyses (id, timestamp, total_severity, problems_count, tier_id, tier_label, image_path, result_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (analysis_id, datetime.datetime.now().isoformat(), result['total_severity'], result['problems_count'],
         result['tier']['id'], result['tier']['label'], filepath, json.dumps(result))
    )

    if compare_with and compare_with != analysis_id:
        existing = db.execute('SELECT id FROM analyses WHERE id = ?', (compare_with,)).fetchone()
        if existing:
            comp_id = uuid.uuid4().hex
            improvement = max(0, result['total_severity'])
            db.execute(
                'INSERT INTO before_after (id, before_id, after_id, timestamp, improvement) VALUES (?, ?, ?, ?, ?)',
                (comp_id, compare_with, analysis_id, datetime.datetime.now().isoformat(), improvement)
            )
            result['compare_id'] = comp_id

    db.commit()
    result['analysis_id'] = analysis_id
    return jsonify(result)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/history/<filename>')
def history_file(filename):
    return send_from_directory(app.config['HISTORY_FOLDER'], filename)


@app.errorhandler(413)
def request_entity_too_large(_e):
    return jsonify({"error": "Файл слишком большой. Максимум 16MB."}), 413


@app.errorhandler(500)
def internal_error(_e):
    return jsonify({"error": "Внутренняя ошибка сервера."}), 500


if __name__ == '__main__':
    init_db()
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
