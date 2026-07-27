<div align="center">
  <h1>FaceAnalyzer</h1>
  <p><strong>AI-powered facial skin analysis & recommendation engine</strong></p>

  <p>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Flask-3.1-lightgrey?logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/MediaPipe-0.10-important?logo=google" alt="MediaPipe">
    <img src="https://img.shields.io/badge/OpenCV-4.10-5C3EE8?logo=opencv" alt="OpenCV">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status">
  </p>

  <br>
</div>

## Overview

FaceAnalyzer is a web application that detects facial landmarks using **MediaPipe FaceMesh**, analyzes skin conditions across multiple zones, and provides personalized skincare recommendations.

Upload a photo — get a detailed breakdown of acne, redness, pores, wrinkles, dark circles, and facial asymmetry with severity scores and product suggestions.

## Features

- **6 analysis types**: acne, redness, pores, wrinkles, dark circles, asymmetry
- **Zone‑aware detection**: forehead, cheeks, nose, chin, under‑eyes
- **Visual overlay**: problem zones highlighted directly on the uploaded photo
- **Severity scoring**: 0–100% per problem + overall score
- **Chad tier**: ranks your result into Truecel → Sub3 → Sub5 → LNT → MTN → HTN → Chad
- **Smart acne filtering**: HSV masking + morphology + circularity + dark‑center check
- **Rotation‑compensated asymmetry**: affine transform based on eye positions
- **Adaptive wrinkle detection**: Canny thresholds adjust to image brightness
- **Dark circles**: compared against overall face skin tone, not the background
- **Rate limiting**: 10 requests/minute per IP
- **Auto‑cleanup**: old uploads removed after 1 hour
- **Beautiful UI**: glassmorphism design, animated background, smooth transitions

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+, Flask 3.1 |
| Face mesh | MediaPipe 0.10 (FaceMesh) |
| Image processing | OpenCV 4.10, NumPy 2.1 |
| Frontend | Vanilla JS, CSS3 (glassmorphism) |
| Templates | Jinja2 |

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/pefkez/face-analyzer.git
cd face-analyzer

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate    # Linux / macOS
# venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py

# 5. Open in your browser
# http://localhost:5000
```

## Usage

1. Upload a front‑facing photo (PNG, JPG, or WEBP, max 16 MB)
2. Wait a few seconds while the AI processes the image
3. View the results:
   - **Summary cards**: overall score, problem count, Chad tier
   - **Overlay**: coloured rectangles on the detected problem zones
   - **Problems list**: click any item for causes, solutions, and product recommendations
   - **Modal**: detailed information per problem type

## API

### `POST /analyze`

Upload a photo for analysis.

**Request**: `multipart/form-data` with field `photo`

**Response** (200):
```json
{
  "total_severity": 34,
  "problems_count": 3,
  "tier": { "id": "mtn", "label": "MTN", "color": "#ffd740" },
  "problems": [
    { "type": "acne", "severity": 45, "zone": "forehead" }
  ],
  "problem_zones": [
    { "type": "acne", "label": "Акне", "x": 120, "y": 80, "w": 30, "h": 30, "severity": 45 }
  ],
  "image_url": "/uploads/abc123.jpg",
  "image_width": 640,
  "image_height": 480
}
```

## Configuration

Set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `0` | Enable Flask debug mode (`1` to enable) |

## Chad Tier System

| Severity | Tier |
|----------|------|
| 0–9 | **Chad** |
| 10–24 | **HTN** |
| 25–39 | **MTN** |
| 40–54 | **LNT** |
| 55–69 | **Sub5** |
| 70–84 | **Sub3** |
| 85–100 | **Truecel** |

## License

Distributed under the MIT License. See `LICENSE` for more information.
