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

const TRANSLATIONS = {
    ru: {
        header_desc: 'Загрузите фото лица — получите анализ кожи и рекомендации',
        upload_text: 'Перетащите фото сюда или <span class="link">выберите файл</span>',
        upload_hint: 'PNG, JPG, WEBP до 16MB. Анфас, хорошее освещение',
        loading_text: 'Анализируем лицо...',
        step1: 'Детекция лица',
        step2: 'Поиск проблемных зон',
        step3: 'Формирование рекомендаций',
        result_title: 'Результаты анализа',
        summary_total: 'Общая оценка',
        summary_problems: 'Проблем найдено',
        summary_tier: 'Тир',
        btn_reset: 'Анализировать другое фото',
        btn_compare: 'Сравнить с предыдущим',
        error_title: 'Ошибка',
        btn_retry: 'Попробовать снова',
        upload_error_format: 'Пожалуйста, выберите изображение в формате PNG или JPG.',
        upload_error_size: 'Файл слишком большой. Максимальный размер — 16MB.',
        server_error: 'Сервер не отвечает. Попробуйте снова.',
        connection_error: 'Ошибка соединения с сервером. Попробуйте снова.',
        acne: 'Акне и воспаления',
        dark_circles: 'Тёмные круги',
        redness: 'Покраснения',
        pores: 'Расширенные поры',
        wrinkles: 'Морщины',
        asymmetry: 'Асимметрия',
        forehead: 'Лоб',
        left_cheek: 'Левая щека',
        right_cheek: 'Правая щека',
        nose: 'Нос',
        chin: 'Подбородок',
        under_eyes: 'Под глазами',
        all: 'Всё лицо',
        modal_causes: 'Возможные причины',
        modal_recommendations: 'Рекомендации',
        modal_products: 'Рекомендуемые средства',
        modal_buy: 'Купить',
        sections: ' участка',
        nav_analyze: 'Анализ',
        nav_history: 'История',
        nav_compare: 'Сравнение',
    },
    en: {
        header_desc: 'Upload a face photo — get skin analysis & recommendations',
        upload_text: 'Drop photo here or <span class="link">select file</span>',
        upload_hint: 'PNG, JPG, WEBP up to 16MB. Front face, good lighting',
        loading_text: 'Analyzing face...',
        step1: 'Face detection',
        step2: 'Problem zone search',
        step3: 'Generating recommendations',
        result_title: 'Analysis Results',
        summary_total: 'Overall Score',
        summary_problems: 'Issues Found',
        summary_tier: 'Tier',
        btn_reset: 'Analyze another photo',
        btn_compare: 'Compare with previous',
        error_title: 'Error',
        btn_retry: 'Try again',
        upload_error_format: 'Please select a PNG or JPG image.',
        upload_error_size: 'File too large. Maximum size is 16MB.',
        server_error: 'Server is not responding. Please try again.',
        connection_error: 'Connection error. Please try again.',
        acne: 'Acne & Inflammation',
        dark_circles: 'Dark Circles',
        redness: 'Redness',
        pores: 'Enlarged Pores',
        wrinkles: 'Wrinkles',
        asymmetry: 'Asymmetry',
        forehead: 'Forehead',
        left_cheek: 'Left Cheek',
        right_cheek: 'Right Cheek',
        nose: 'Nose',
        chin: 'Chin',
        under_eyes: 'Under Eyes',
        all: 'Full Face',
        modal_causes: 'Possible Causes',
        modal_recommendations: 'Recommendations',
        modal_products: 'Recommended Products',
        modal_buy: 'Buy',
        sections: ' sections',
        nav_analyze: 'Analyze',
        nav_history: 'History',
        nav_compare: 'Compare',
    }
};

const EN_DESCRIPTIONS = {
    acne: {
        label: 'Acne & Inflammation',
        description: 'Redness and inflamed areas detected on the face.',
        causes: ['Hormonal changes', 'Improper skincare', 'High-sugar diet', 'Stress'],
        solutions: ['Use salicylic acid toner 2x daily', 'Apply benzoyl peroxide (2.5%) spot treatment', 'Wash with gentle pH 5.5 cleanser', 'Consult a dermatologist'],
        products: ['Salicylic Acid 2%', 'Benzoyl Peroxide 2.5%', 'Zinc Cleanser']
    },
    dark_circles: {
        label: 'Dark Circles',
        description: 'The under-eye area has a darker shade than the rest of the face.',
        causes: ['Lack of sleep', 'Allergies', 'Dehydration', 'Age-related changes', 'Genetics'],
        solutions: ['Sleep 7-8 hours per night', 'Use caffeine & vitamin K eye cream', 'Lymphatic drainage massage', 'Drink enough water (30ml per kg)'],
        products: ['Caffeine Eye Cream', 'Hydrogel Patches', 'Vitamin C Serum']
    },
    redness: {
        label: 'Redness & Couperose',
        description: 'Areas with increased redness and visible vascular network.',
        causes: ['Sensitive skin', 'Couperose', 'Rosacea', 'Harsh cosmetics'],
        solutions: ['Use niacinamide & panthenol products', 'Avoid scrubs and alcohol toners', 'Apply SPF 50 daily', 'Use thermal water'],
        products: ['Niacinamide 5%', 'Cica Cream', 'SPF 50+']
    },
    asymmetry: {
        label: 'Facial Asymmetry',
        description: 'Slight asymmetry between the left and right sides of the face.',
        causes: ['Natural feature', 'One-sided chewing habit', 'Poor posture', 'Muscle tension'],
        solutions: ['Do face yoga (facebuilding)', 'Chew evenly on both sides', 'Watch your posture', 'Facial massage to relax muscles'],
        products: ['Gua Sha Tool', 'Facial Massage Oil']
    },
    pores: {
        label: 'Enlarged Pores',
        description: 'Pores are noticeably enlarged, especially in the T-zone.',
        causes: ['Increased sebum production', 'Age-related changes', 'Improper cleansing', 'Sun damage'],
        solutions: ['Use niacinamide 5-10% serum', 'Gentle enzyme peel 1-2x/week', 'Apply SPF 50 daily', 'Wash with AHA acids'],
        products: ['Niacinamide 10%', 'Enzyme Powder', 'AHA Toner 5%']
    },
    wrinkles: {
        label: 'Expression Wrinkles',
        description: 'Lines and wrinkles detected on the forehead, around eyes, and nasolabial area.',
        causes: ['Age-related changes', 'Active facial expressions', 'Sun damage', 'Skin dehydration', 'Smoking'],
        solutions: ['Use retinol (start with 0.25-0.5%)', 'Apply hyaluronic acid moisturizer', 'SPF 50 — mandatory every day', 'Take collagen supplements'],
        products: ['Retinol 0.3%', 'Hyaluronic Acid', 'SPF 50+']
    }
};

let currentLang = 'ru';
let currentData = null;
let lastAnalysisId = null;
let compareMode = false;

function t(key) {
    const val = TRANSLATIONS[currentLang][key];
    return val !== undefined ? val : key;
}

function translatePage() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        el.innerHTML = t(key);
    });
    if (currentData) {
        showResults(currentData);
    }
}

function switchLanguage(lang) {
    if (lang === currentLang) return;
    currentLang = lang;
    document.querySelectorAll('.lang-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.lang === lang);
    });
    document.documentElement.lang = lang === 'ru' ? 'ru' : 'en';
    translatePage();
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => switchLanguage(btn.dataset.lang));
    });

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

    const params = new URLSearchParams(location.search);
    if (params.get('load')) {
        loadHistoryAnalysis(params.get('load'));
    }
});

async function loadHistoryAnalysis(id) {
    try {
        const r = await fetch(`/api/history/${id}`);
        const data = await r.json();
        if (data.error) return;
        document.getElementById('upload-section').classList.add('hidden');
        showResults({ ...data.result, image_url: '/' + data.image_path.replace(/\\/g, '/'), analysis_id: data.id });
    } catch(e) {}
}

function uploadFile(file) {
    if (!file.type.match(/^image\/(png|jpeg|webp)$/)) {
        showError(t('upload_error_format'));
        return;
    }
    if (file.size > 16 * 1024 * 1024) {
        showError(t('upload_error_size'));
        return;
    }

    document.getElementById('upload-section').classList.add('hidden');
    document.getElementById('loading-section').classList.remove('hidden');

    const formData = new FormData();
    formData.append('photo', file);

    if (compareMode && lastAnalysisId) {
        formData.append('compare_with', lastAnalysisId);
    }

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
                showError(data.error || t('connection_error'));
                return;
            }
            compareMode = false;
            showResults(data);
        })
        .catch((err) => {
            clearTimeout(timeoutId);
            if (err.name === 'AbortError') {
                showError(t('server_error'));
                return;
            }
            if (attempt < MAX_RETRIES) {
                setTimeout(() => sendWithRetry(url, body, attempt + 1), 1000 * (attempt + 1));
            } else {
                document.getElementById('loading-section').classList.add('hidden');
                showError(t('connection_error'));
            }
        });
}

function showResults(data) {
    currentData = data;
    lastAnalysisId = data.analysis_id;
    document.getElementById('result-section').classList.remove('hidden');

    const cards = document.querySelectorAll('.summary-card');
    cards.forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(12px)';
        requestAnimationFrame(() => {
            card.style.transition = `opacity 0.35s ease-out ${i * 0.06}s, transform 0.35s ease-out ${i * 0.06}s`;
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        });
    });

    const resultBody = document.querySelector('.result-body');
    if (resultBody) {
        resultBody.style.opacity = '0';
        resultBody.style.transform = 'translateY(16px)';
        requestAnimationFrame(() => {
            resultBody.style.transition = 'opacity 0.4s ease-out 0.2s, transform 0.4s ease-out 0.2s';
            resultBody.style.opacity = '1';
            resultBody.style.transform = 'translateY(0)';
        });
    }

    document.getElementById('totalSeverity').textContent = data.total_severity + '%';
    document.getElementById('problemsCount').textContent = data.problems_count;

    const resetBtn = document.querySelector('#result-section > .btn');
    if (resetBtn) {
        resetBtn.style.opacity = '0';
        resetBtn.style.transform = 'translateY(8px)';
        requestAnimationFrame(() => {
            resetBtn.style.transition = 'opacity 0.3s ease-out 0.3s, transform 0.3s ease-out 0.3s';
            resetBtn.style.opacity = '1';
            resetBtn.style.transform = 'translateY(0)';
        });
    }

    const tierEl = document.getElementById('tierValue');
    const tierCard = document.getElementById('tierCard');
    if (data.tier) {
        tierEl.textContent = data.tier.label;
        tierEl.style.color = data.tier.color;
        tierCard.style.borderColor = data.tier.color;
    }

    const compareBtn = document.getElementById('btnCompare');
    if (compareBtn) {
        compareBtn.classList.remove('hidden');
        compareBtn.textContent = t('btn_compare');
    }

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

    data.problem_zones.forEach((zone) => {
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
    return t(type);
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
        let zoneName = zone.type === 'asymmetry' ? t('all') : (t(zone.zone) || zone.zone || '');
        const countText = zone.count > 1 ? ` (${zone.count}${t('sections')})` : '';
        item.innerHTML = `
            <div class="problem-header">
                <span class="problem-name">${getTypeLabel(zone.type)}</span>
                <span class="problem-severity">${zone.maxSeverity}%</span>
            </div>
            <div class="problem-zone">${zoneName}${countText}</div>
        `;
        item.addEventListener('click', () => openModal(zone));
        list.appendChild(item);
    });
}

function openModal(zone) {
    const modal = document.getElementById('problemModal');
    const body = document.getElementById('modalBody');
    const d = (currentLang === 'en' && EN_DESCRIPTIONS[zone.type])
        ? EN_DESCRIPTIONS[zone.type]
        : zone.data;

    const hasAffiliate = d.affiliate_links && d.affiliate_links.length > 0;

    let severityColor = zone.severity > 60 ? COLORS.red : zone.severity > 30 ? COLORS.orange : COLORS.yellow;

    let productsHtml = d.products.map((p, i) => {
        if (hasAffiliate && d.affiliate_links[i]) {
            return `<a href="${d.affiliate_links[i]}" target="_blank" rel="noopener" class="product-tag product-link">${p} ↗</a>`;
        }
        return `<span class="product-tag">${p}</span>`;
    }).join('');

    body.innerHTML = `
        <h2>${d.label}</h2>
        <div class="severity-bar">
            <div class="bar">
                <div class="bar-fill" style="width:${zone.severity}%;background:${severityColor}"></div>
            </div>
            <span class="severity-label">${zone.severity}%</span>
        </div>
        <p class="modal-desc">${d.description}</p>
        <div class="modal-section">
            <h3>${t('modal_causes')}</h3>
            <ul>${d.causes.map(c => `<li>${c}</li>`).join('')}</ul>
        </div>
        <div class="modal-section">
            <h3>${t('modal_recommendations')}</h3>
            <ul>${d.solutions.map(s => `<li>${s}</li>`).join('')}</ul>
        </div>
        <div class="modal-section">
            <h3>${t('modal_products')}</h3>
            <div>${productsHtml}</div>
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
    document.getElementById('tierValue').textContent = '—';
    document.getElementById('tierValue').style.color = '';
    document.getElementById('tierCard').style.borderColor = '';
    const compareBtn = document.getElementById('btnCompare');
    if (compareBtn) compareBtn.classList.add('hidden');
    compareMode = false;
    currentData = null;
}

function setCompareMode() {
    if (!lastAnalysisId) return;
    compareMode = true;
    const btn = document.getElementById('btnCompare');
    btn.textContent = '📸 ' + (currentLang === 'ru' ? 'Загрузите новое фото для сравнения' : 'Upload new photo to compare');
    btn.classList.add('compare-active');
    document.getElementById('faceImage').src = '';
    document.getElementById('overlay').innerHTML = '';
    document.getElementById('problemsList').innerHTML = '';
    document.getElementById('legend').innerHTML = '';
    document.getElementById('upload-section').classList.remove('hidden');
}
