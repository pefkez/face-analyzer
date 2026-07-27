import os
import uuid
import time
import threading
from pathlib import Path
from collections import defaultdict
from flask import Flask, render_template, request, jsonify, send_from_directory
from analyzer import analyze_face

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['CLEANUP_MAX_AGE'] = 3600
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

RATE_LIMIT = 10
RATE_WINDOW = 60
_rate_store = defaultdict(list)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

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

    result = analyze_face(filepath)

    if "error" in result:
        os.remove(filepath)
        return jsonify(result), 400

    result["image_url"] = f"/uploads/{filename}"
    return jsonify(result)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)