# TruecelAnalyzer

Загружаешь фото — получаешь разбор кожи: акне, покраснения, поры, морщины, синяки под глазами, асимметрия. С оценками от Truecel до Chad.

```
pip install -r requirements.txt
python app.py
```

Открыть http://localhost:5000, загрузить фото (PNG/JPG/WEBP, до 16 MB).

Есть и API: `POST /analyze` принимает multipart/form-data с полем `photo` и возвращает severity по каждому типу проблем + координаты зон на изображении.

Если нужно, `FLASK_DEBUG=1` включает debug mode.
