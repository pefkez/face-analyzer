# TruecelAnalyzer

Загружаешь фото — получаешь разбор кожи: акне, покраснения, поры, морщины, синяки под глазами, асимметрия. С оценками от Truecel до Chad.

```
pip install -r requirements.txt
python app.py
```

Открыть http://localhost:5000, загрузить фото (PNG/JPG/WEBP, до 16 MB).

### API

```
POST /analyze
multipart/form-data с полем photo
```

Возвращает severity по каждому типу проблем + координаты зон на изображении.

### Переменные окружения

`FLASK_DEBUG=1` — включить debug mode.
