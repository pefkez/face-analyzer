const COLORS = {
    acne: '#ff6b6b',
    dark_circles: '#6c5ce7',
    redness: '#ff7675',
    pores: '#fdcb6e',
    wrinkles: '#81ecec',
    asymmetry: '#a29bfe',
    red: '#ff6b6b',
    orange: '#ffa94d',
    yellow: '#ffd43b'
};

const REQUEST_TIMEOUT = 30000;
const MAX_RETRIES = 2;

const ZONE_NAMES = {
    forehead: 'Лоб',
    left_cheek: 'Левая щека',
    right_cheek: 'Правая щека',
    nose: 'Нос',
    chin: 'Подбородок',
    under_eyes: 'Под глазами',
    all: 'Всё лицо'
};

let currentData = null;

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) uploadFile(files[0]);
    });
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) uploadFile(e.target.files[0]);
    });
});

function uploadFile(file) {
    if (!file.type.match(/^image\/(png|jpeg|webp)$/)) {
        showError('Пожалуйста, выберите изображение в формате PNG или JPG.');
        return;
    }
    if (file.size > 16 * 1024 * 1024) {
        showError('Файл слишком большой. Максимальный размер — 16MB.');
        return;
    }

    document.getElementById('upload-section').classList.add('hidden');
    document.getElementById('loading-section').classList.remove('hidden');

    const formData = new FormData();
    formData.append('photo', file);

    sendWithRetry('/analyze', formData, 0);
}

function sendWithRetry(url, body, attempt) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    fetch(url, { method: 'POST', body, signal: controller.signal })
        .then(r => r.json().then(data => ({ ok: r.ok, data })))
        .then(({ ok, data }) => {
            clearTimeout(timeoutId);
            document.getElementById('loading-section').classList.add('hidden');
            if (!ok || data.error) {
                showError(data.error || 'Неизвестная ошибка.');
                return;
            }
            showResults(data);
        })
        .catch((err) => {
            clearTimeout(timeoutId);
            if (err.name === 'AbortError') {
                showError('Сервер не отвечает. Попробуйте снова.');
                return;
            }
            if (attempt < MAX_RETRIES) {
                setTimeout(() => sendWithRetry(url, body, attempt + 1), 1000 * (attempt + 1));
            } else {
                document.getElementById('loading-section').classList.add('hidden');
                showError('Ошибка соединения с сервером. Попробуйте снова.');
            }
        });
}

function showResults(data) {
    currentData = data;
    document.getElementById('result-section').classList.remove('hidden');

    document.getElementById('totalSeverity').textContent = data.total_severity + '%';
    document.getElementById('problemsCount').textContent = data.problems_count;

    const img = document.getElementById('faceImage');
    img.src = data.image_url;
    img.onload = () => renderOverlay(data);
}

function renderOverlay(data) {
    const overlay = document.getElementById('overlay');
    const legend = document.getElementById('legend');
    overlay.innerHTML = '';
    legend.innerHTML = '';

    const img = document.getElementById('faceImage');
    const scaleX = img.clientWidth / data.image_width;
    const scaleY = img.clientHeight / data.image_height;

    const seenTypes = new Set();

    data.problem_zones.forEach((zone, index) => {
        seenTypes.add(zone.type);

        const el = document.createElement('div');
        el.className = `zone-rect ${zone.type}`;
        el.style.left = (zone.x * scaleX) + 'px';
        el.style.top = (zone.y * scaleY) + 'px';
        el.style.width = (zone.w * scaleX) + 'px';
        el.style.height = (zone.h * scaleY) + 'px';
        el.title = zone.label;
        el.addEventListener('click', () => openModal(zone));
        overlay.appendChild(el);
    });

    seenTypes.forEach(type => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `<span class="legend-color" style="background:${COLORS[type] || '#fff'}"></span>${getTypeLabel(type)}`;
        legend.appendChild(item);
    });

    renderProblemsList(data);
}

function getTypeLabel(type) {
    const labels = {
        acne: 'Акне',
        dark_circles: 'Тёмные круги',
        redness: 'Покраснения',
        pores: 'Расширенные поры',
        wrinkles: 'Морщины',
        asymmetry: 'Асимметрия'
    };
    return labels[type] || type;
}

function renderProblemsList(data) {
    const list = document.getElementById('problemsList');
    list.innerHTML = '';

    const grouped = {};
    data.problem_zones.forEach(z => {
        if (!grouped[z.type]) {
            grouped[z.type] = { ...z, count: 0, maxSeverity: 0 };
        }
        grouped[z.type].count++;
        if (z.severity > grouped[z.type].maxSeverity) {
            grouped[z.type].maxSeverity = z.severity;
            grouped[z.type].severity = z.severity;
            grouped[z.type].data = z.data;
            grouped[z.type].label = z.label;
        }
    });

    Object.values(grouped).forEach(zone => {
        const item = document.createElement('div');
        item.className = `problem-item ${zone.type}`;
        let zoneName = zone.type === 'asymmetry' ? 'Всё лицо' : (ZONE_NAMES[zone.zone] || zone.zone || '');
        item.innerHTML = `
            <div class="problem-header">
                <span class="problem-name">${zone.label}</span>
                <span class="problem-severity">${zone.maxSeverity}%</span>
            </div>
            <div class="problem-zone">${zoneName}${zone.count > 1 ? ` (${zone.count} участка)` : ''}</div>
        `;
        item.addEventListener('click', () => openModal(zone));
        list.appendChild(item);
    });
}

function openModal(zone) {
    const modal = document.getElementById('problemModal');
    const body = document.getElementById('modalBody');
    const d = zone.data;

    let severityColor = zone.severity > 60 ? COLORS.red : zone.severity > 30 ? COLORS.orange : COLORS.yellow;

    body.innerHTML = `
        <h2>${zone.label}</h2>
        <div class="severity-bar">
            <div class="bar">
                <div class="bar-fill" style="width:${zone.severity}%;background:${severityColor}"></div>
            </div>
            <span class="severity-label">${zone.severity}%</span>
        </div>
        <p class="modal-desc">${d.description}</p>
        <div class="modal-section">
            <h3>Возможные причины</h3>
            <ul>${d.causes.map(c => `<li>${c}</li>`).join('')}</ul>
        </div>
        <div class="modal-section">
            <h3>Рекомендации</h3>
            <ul>${d.solutions.map(s => `<li>${s}</li>`).join('')}</ul>
        </div>
        <div class="modal-section">
            <h3>Рекомендуемые средства</h3>
            <div>${d.products.map(p => `<span class="product-tag">${p}</span>`).join('')}</div>
        </div>
    `;

    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('problemModal').classList.add('hidden');
}

function showError(msg) {
    document.getElementById('error-section').classList.remove('hidden');
    document.getElementById('errorMessage').textContent = msg;
}

function resetApp() {
    document.getElementById('upload-section').classList.remove('hidden');
    document.getElementById('result-section').classList.add('hidden');
    document.getElementById('error-section').classList.add('hidden');
    document.getElementById('loading-section').classList.add('hidden');
    document.getElementById('faceImage').src = '';
    document.getElementById('overlay').innerHTML = '';
    document.getElementById('problemsList').innerHTML = '';
    document.getElementById('legend').innerHTML = '';
    document.getElementById('problemModal').classList.add('hidden');
    document.getElementById('fileInput').value = '';
    currentData = null;
}