import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
LEFT_CHEEK = [50, 101, 100, 99, 98, 97, 115, 116, 117, 118, 119, 120, 121, 126, 205, 206, 207, 208, 210]
RIGHT_CHEEK = [280, 330, 329, 328, 327, 326, 345, 346, 347, 348, 349, 350, 351, 352, 425, 426, 427, 428, 429]
FOREHEAD = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378]
NOSE = [1, 2, 3, 4, 5, 6, 19, 20, 44, 45, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96]
CHIN = [130, 129, 128, 127, 125, 124, 123, 122, 143, 140, 137, 135, 134, 132, 131]
UNDER_LEFT_EYE = [160, 159, 158, 157, 173, 154, 153, 145, 144, 163, 7]
UNDER_RIGHT_EYE = [386, 385, 384, 398, 466, 263, 249, 390, 373, 374, 380]

FACE_OVERALL = (LEFT_CHEEK + RIGHT_CHEEK + FOREHEAD + NOSE + CHIN +
    [0, 11, 12, 13, 14, 15, 16, 17, 18, 37, 38, 39, 40, 41, 42, 43,
     180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195,
     196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211,
     212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227,
     228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243,
     244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259,
     260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275,
     276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291,
     292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307,
     308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323,
     324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339,
     340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355,
     356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371,
     372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387,
     388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403,
     404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419,
     420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435,
     436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451,
     452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467])

SYMMETRIC_PAIRS = [
    (33, 263), (7, 382), (163, 381), (144, 380), (145, 374), (153, 373),
    (154, 390), (155, 249), (133, 362), (173, 466), (157, 388), (158, 387),
    (159, 386), (160, 385), (161, 384), (246, 398),
    (50, 280), (101, 330), (100, 329), (99, 328), (98, 327), (97, 326),
    (115, 345), (116, 346), (117, 347), (118, 348), (119, 349), (120, 350),
    (121, 351), (126, 352), (205, 425), (206, 426), (207, 427), (208, 428), (210, 429),
]

PROBLEM_DESCRIPTIONS = {
    "acne": {
        "label": "Акне и воспаления",
        "description": "На лице обнаружены покраснения и воспалённые участки.",
        "causes": ["Гормональные изменения", "Неправильный уход за кожей", "Питание с высоким содержанием сахара", "Стресс"],
        "solutions": [
            "Используйте салициловую кислоту в тонике 2 раза в день",
            "Наносите бензоилпероксид (2.5%) точечно на воспаления",
            "Умывайтесь мягким гелем с pH 5.5",
            "Посетите дерматолога для подбора терапии"
        ],
        "products": ["Салициловая кислота 2%", "Бензоилпероксид 2.5%", "Гель для умывания с цинком"]
    },
    "dark_circles": {
        "label": "Тёмные круги под глазами",
        "description": "Область под глазами имеет более тёмный оттенок.",
        "causes": ["Недостаток сна", "Аллергия", "Обезвоживание", "Возрастные изменения", "Наследственность"],
        "solutions": [
            "Спите не менее 7-8 часов в сутки",
            "Используйте крем с кофеином и витамином К",
            "Делайте лимфодренажный массаж",
            "Пейте достаточно воды (30 мл на кг веса)"
        ],
        "products": ["Крем с кофеином для век", "Патчи гидрогелевые", "Сыворотка с витамином С"]
    },
    "redness": {
        "label": "Покраснения и купероз",
        "description": "На коже заметны участки с повышенной краснотой и сосудистой сеткой.",
        "causes": ["Чувствительная кожа", "Купероз (сосудистая сетка)", "Розацеа", "Агрессивные косметические средства"],
        "solutions": [
            "Используйте средства с ниацинамидом и пантенолом",
            "Избегайте скрабов и спиртовых тоников",
            "Наносите SPF 50 ежедневно",
            "Умойтесь и используйте термальную воду"
        ],
        "products": ["Ниацинамид 5%", "Крем с центеллой азиатской", "SPF 50+"]
    },
    "asymmetry": {
        "label": "Асимметрия лица",
        "description": "Заметна небольшая асимметрия между левой и правой сторонами лица.",
        "causes": ["Естественная особенность", "Привычка жевать на одну сторону", "Неправильная осанка", "Мышечное напряжение"],
        "solutions": [
            "Делайте гимнастику для лица (фейсбилдинг)",
            "Старайтесь жевать равномерно на обе стороны",
            "Следите за осанкой",
            "Массаж лица для расслабления мышц"
        ],
        "products": ["Гуаша для массажа", "Масло для массажа лица"]
    },
    "pores": {
        "label": "Расширенные поры",
        "description": "Поры на лице заметно расширены, особенно в Т-зоне.",
        "causes": ["Повышенная выработка себума", "Возрастные изменения", "Неправильное очищение", "Солнечное повреждение"],
        "solutions": [
            "Используйте сыворотку с ниацинамидом 5-10%",
            "Делайте мягкие энзимные пилинги 1-2 раза в неделю",
            "Наносите SPF 50 ежедневно",
            "Умывайтесь с AHA-кислотами"
        ],
        "products": ["Ниацинамид 10%", "Энзимная пудра", "AHA-тоник 5%"]
    },
    "wrinkles": {
        "label": "Мимические морщины",
        "description": "Обнаружены линии и морщины в области лба, глаз и носогубного треугольника.",
        "causes": ["Возрастные изменения", "Активная мимика", "Солнечное повреждение", "Обезвоживание кожи", "Курение"],
        "solutions": [
            "Используйте ретинол (начать с 0.25-0.5%)",
            "Наносите увлажняющий крем с гиалуроновой кислотой",
            "SPF 50 — обязателен каждый день",
            "Пейте коллаген в добавках"
        ],
        "products": ["Ретинол 0.3%", "Гиалуроновая кислота", "SPF 50+"]
    }
}

def get_landmark_coords(landmarks, idx, w, h):
    lm = landmarks[idx]
    return int(lm.x * w), int(lm.y * h)

def get_region_mask(h, w, landmarks, region_indices):
    mask = np.zeros((h, w), dtype=np.uint8)
    points = []
    for idx in region_indices:
        if idx < len(landmarks):
            x, y = get_landmark_coords(landmarks, idx, w, h)
            points.append([x, y])
    if points:
        hull = cv2.convexHull(np.array(points))
        cv2.fillConvexPoly(mask, hull, 255)
    return mask

def detect_acne(roi, mask):
    if mask is None or cv2.countNonZero(mask) < 50:
        return []
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 40, 40])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([165, 40, 40])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    red_mask = cv2.bitwise_and(red_mask, mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    spots = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 8 or area > 500:
            continue
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity > 0.85:
            continue

        x, y, sw, sh = cv2.boundingRect(cnt)
        spot_roi = roi[y:y+sh, x:x+sw]
        if spot_roi.size == 0:
            continue

        gray_spot = cv2.cvtColor(spot_roi, cv2.COLOR_BGR2GRAY)
        center_region = gray_spot[sh//4:3*sh//4, sw//4:3*sw//4]
        if center_region.size == 0:
            continue
        center_mean = np.mean(center_region)
        spot_mean = np.mean(gray_spot)
        if center_mean >= spot_mean + 3:
            continue

        spots.append({"x": x, "y": y, "w": sw, "h": sh, "area": int(area)})
    return spots

def detect_dark_circles(roi, mask, face_mask=None):
    if mask is None or cv2.countNonZero(mask) < 50:
        return None
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    under_eyes_mean = cv2.mean(gray, mask)[0]

    if face_mask is not None and cv2.countNonZero(face_mask) > 100:
        face_mean = cv2.mean(gray, face_mask)[0]
    else:
        face_mean = cv2.mean(gray)[0]
    if face_mean < 1:
        face_mean = 128

    diff = face_mean - under_eyes_mean
    severity = min(100, max(0, int(diff * 2.5 * (face_mean / 128))))
    return severity

def detect_redness(roi, mask):
    if mask is None or cv2.countNonZero(mask) < 50:
        return None
    b, g, r = cv2.split(roi)
    r_mean = cv2.mean(r, mask)[0]
    g_mean = cv2.mean(g, mask)[0]
    ratio = r_mean / max(g_mean, 1)
    severity = min(100, max(0, int((ratio - 1.05) * 200)))
    return severity

def detect_pores(roi, mask):
    if mask is None or cv2.countNonZero(mask) < 50:
        return None
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = cv2.mean(laplacian ** 2, mask)[0]
    severity = min(100, max(0, int(variance / 15)))
    return severity

def detect_wrinkles(roi, mask):
    if mask is None or cv2.countNonZero(mask) < 50:
        return None
    try:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        mean_intensity = cv2.mean(blurred, mask)[0]
        low_thresh = max(10, int(mean_intensity * 0.15))
        high_thresh = max(30, int(mean_intensity * 0.4))
        edges = cv2.Canny(blurred, low_thresh, high_thresh)
        edges = cv2.bitwise_and(edges, mask)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, minLineLength=15, maxLineGap=8)
        severity = 0
        if lines is not None and len(lines) > 0:
            total_len = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                total_len += np.hypot(x2 - x1, y2 - y1)
            severity = min(100, int(total_len / 15))
        return severity
    except Exception:
        return None

def analyze_asymmetry(landmarks, w, h):
    try:
        left_eye_x = np.mean([landmarks[i].x for i in [33, 133]])
        left_eye_y = np.mean([landmarks[i].y for i in [33, 133]])
        right_eye_x = np.mean([landmarks[i].x for i in [362, 263]])
        right_eye_y = np.mean([landmarks[i].y for i in [362, 263]])

        angle = -np.degrees(np.arctan2(right_eye_y - left_eye_y, right_eye_x - left_eye_x))

        cx, cy = w / 2.0, h / 2.0
        M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)

        left_dists = []
        right_dists = []

        for left_idx, right_idx in SYMMETRIC_PAIRS:
            if left_idx >= len(landmarks) or right_idx >= len(landmarks):
                continue
            lx = landmarks[left_idx].x * w
            ly = landmarks[left_idx].y * h
            rx = landmarks[right_idx].x * w
            ry = landmarks[right_idx].y * h

            lxr = M[0, 0] * lx + M[0, 1] * ly + M[0, 2]
            rxr = M[0, 0] * rx + M[0, 1] * ry + M[0, 2]
            left_dists.append(abs(lxr - cx))
            right_dists.append(abs(rxr - cx))

        if len(left_dists) < 3 or len(right_dists) < 3:
            return 0

        left_mean = np.mean(left_dists)
        right_mean = np.mean(right_dists)
        divisor = max(left_mean, right_mean)
        if divisor < 1:
            return 0
        ratio = min(left_mean, right_mean) / divisor
        severity = min(100, max(0, int((1 - ratio) * 180)))
        return severity
    except Exception:
        return 0

def analyze_face(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "Не удалось загрузить изображение. Файл повреждён или имеет неподдерживаемый формат."}

    try:
        if img.shape[0] < 10 or img.shape[1] < 10:
            return {"error": "Изображение слишком маленькое."}
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except Exception:
        return {"error": "Ошибка обработки изображения. Возможно, файл битый."}

    h, w, _ = img.shape

    problems = []
    problem_zones = []

    try:
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
            results = face_mesh.process(img_rgb)
            if not results.multi_face_landmarks:
                return {"error": "Лицо не обнаружено. Попробуйте другое фото."}

            landmarks = results.multi_face_landmarks[0].landmark
    except Exception:
        return {"error": "Ошибка при анализе лица. Попробуйте другое изображение."}

        asymmetry = analyze_asymmetry(landmarks, w, h)
        if asymmetry > 15:
            problems.append({"type": "asymmetry", "severity": asymmetry, "zone": "all"})
            problem_zones.append({
                "type": "asymmetry",
                "label": PROBLEM_DESCRIPTIONS["asymmetry"]["label"],
                "x": w // 4, "y": h // 4, "w": w // 2, "h": h // 2,
                "severity": asymmetry,
                "data": PROBLEM_DESCRIPTIONS["asymmetry"]
            })

        face_mask = get_region_mask(h, w, landmarks, FACE_OVERALL)

        regions = [
            {"name": "forehead", "indices": FOREHEAD, "check": ["acne", "redness", "pores", "wrinkles"]},
            {"name": "left_cheek", "indices": LEFT_CHEEK, "check": ["acne", "redness", "pores"]},
            {"name": "right_cheek", "indices": RIGHT_CHEEK, "check": ["acne", "redness", "pores"]},
            {"name": "nose", "indices": NOSE, "check": ["acne", "redness", "pores"]},
            {"name": "chin", "indices": CHIN, "check": ["acne", "redness", "pores"]},
        ]

        for region in regions:
            mask = get_region_mask(h, w, landmarks, region["indices"])
            if cv2.countNonZero(mask) < 50:
                continue

            x, y, rw, rh = cv2.boundingRect(mask)
            roi = img[y:y+rh, x:x+rw]
            roi_mask = mask[y:y+rh, x:x+rw]

            for check in region["check"]:
                try:
                    if check == "acne":
                        spots = detect_acne(roi, roi_mask)
                        for spot in spots:
                            sx, sy = x + spot["x"], y + spot["y"]
                            problems.append({"type": "acne", "severity": min(100, spot["area"]), "zone": region["name"], "x": sx, "y": sy})
                            problem_zones.append({
                                "type": "acne",
                                "label": "Акне",
                                "x": sx, "y": sy, "w": spot["w"], "h": spot["h"],
                                "severity": min(100, spot["area"]),
                                "data": PROBLEM_DESCRIPTIONS["acne"]
                            })

                    elif check == "redness":
                        severity = detect_redness(roi, roi_mask)
                        if severity and severity > 20:
                            problems.append({"type": "redness", "severity": severity, "zone": region["name"]})
                            problem_zones.append({
                                "type": "redness",
                                "label": PROBLEM_DESCRIPTIONS["redness"]["label"],
                                "x": x, "y": y, "w": rw, "h": rh,
                                "severity": severity,
                                "data": PROBLEM_DESCRIPTIONS["redness"]
                            })

                    elif check == "pores":
                        severity = detect_pores(roi, roi_mask)
                        if severity and severity > 25:
                            problems.append({"type": "pores", "severity": severity, "zone": region["name"]})
                            problem_zones.append({
                                "type": "pores",
                                "label": PROBLEM_DESCRIPTIONS["pores"]["label"],
                                "x": x, "y": y, "w": rw, "h": rh,
                                "severity": severity,
                                "data": PROBLEM_DESCRIPTIONS["pores"]
                            })

                    elif check == "wrinkles":
                        severity = detect_wrinkles(roi, roi_mask)
                        if severity and severity > 20:
                            problems.append({"type": "wrinkles", "severity": severity, "zone": region["name"]})
                            problem_zones.append({
                                "type": "wrinkles",
                                "label": PROBLEM_DESCRIPTIONS["wrinkles"]["label"],
                                "x": x, "y": y, "w": rw, "h": rh,
                                "severity": severity,
                                "data": PROBLEM_DESCRIPTIONS["wrinkles"]
                            })
                except Exception:
                    pass

        under_left_mask = get_region_mask(h, w, landmarks, UNDER_LEFT_EYE)
        under_right_mask = get_region_mask(h, w, landmarks, UNDER_RIGHT_EYE)
        under_eyes_mask = cv2.bitwise_or(under_left_mask, under_right_mask)

        if cv2.countNonZero(under_eyes_mask) > 50:
            lx, ly, lw, lh = cv2.boundingRect(under_left_mask) if cv2.countNonZero(under_left_mask) > 50 else (0, 0, 0, 0)
            rx, ry, rw2, rh2 = cv2.boundingRect(under_right_mask) if cv2.countNonZero(under_right_mask) > 50 else (0, 0, 0, 0)

            try:
                severity = detect_dark_circles(img, under_eyes_mask, face_mask)
            except Exception:
                severity = None
            if severity and severity > 15:
                problems.append({"type": "dark_circles", "severity": severity, "zone": "under_eyes"})
                if lw > 0:
                    problem_zones.append({
                        "type": "dark_circles",
                        "label": PROBLEM_DESCRIPTIONS["dark_circles"]["label"],
                        "x": lx, "y": ly, "w": lw, "h": lh,
                        "severity": severity,
                        "data": PROBLEM_DESCRIPTIONS["dark_circles"]
                    })
                if rw2 > 0:
                    problem_zones.append({
                        "type": "dark_circles",
                        "label": PROBLEM_DESCRIPTIONS["dark_circles"]["label"],
                        "x": rx, "y": ry, "w": rw2, "h": rh2,
                        "severity": severity,
                        "data": PROBLEM_DESCRIPTIONS["dark_circles"]
                    })

    total_severity = 0
    for p in problems:
        total_severity += p["severity"]
    total_severity = min(100, total_severity // max(len(problems), 1)) if problems else 0

    tier = get_chad_tier(total_severity)

    return {
        "problems": problems,
        "problem_zones": problem_zones,
        "total_severity": total_severity,
        "problems_count": len(set(p["type"] for p in problems)),
        "image_width": w,
        "image_height": h,
        "tier": tier
    }


CHAD_TIERS = [
    {"id": "chad", "label": "Chad", "range": (0, 9), "color": "#00e676"},
    {"id": "htn", "label": "HTN", "range": (10, 24), "color": "#69f0ae"},
    {"id": "mtn", "label": "MTN", "range": (25, 39), "color": "#ffd740"},
    {"id": "lnt", "label": "LNT", "range": (40, 54), "color": "#ffab40"},
    {"id": "sub5", "label": "Sub5", "range": (55, 69), "color": "#ff6e40"},
    {"id": "sub3", "label": "Sub3", "range": (70, 84), "color": "#ff3d00"},
    {"id": "truecel", "label": "Truecel", "range": (85, 100), "color": "#d50000"},
]

def get_chad_tier(severity):
    for tier in CHAD_TIERS:
        if tier["range"][0] <= severity <= tier["range"][1]:
            return tier
    return CHAD_TIERS[-1]