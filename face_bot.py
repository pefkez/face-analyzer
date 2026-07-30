import os, io, logging, asyncio, json, uuid
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from analyzer import analyze_face
import cv2
import numpy as np

load_dotenv()
TOKEN = os.getenv("FACE_BOT_TOKEN")
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}
UPLOAD_DIR = Path("bot_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_tier_emoji(tier_id):
    return {
        "chad": "\U0001f451",
        "htn": "\U0001f60e",
        "mtn": "\u2705",
        "lnt": "\u26a0\ufe0f",
        "sub5": "\u274c",
        "sub3": "\U0001f4a5",
        "truecel": "\U0001f480"
    }.get(tier_id, "\u2753")


def format_result(result):
    if "error" in result:
        return f"\u274c {result['error']}"

    tier = result.get('tier', {})
    emoji = make_tier_emoji(tier.get('id', ''))
    lines = [
        f"\U0001f3f7\ufe0f *\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u044b \u0430\u043d\u0430\u043b\u0438\u0437\u0430*",
        f"",
        f"{emoji} \u0422\u0438\u0440: *{tier.get('label', '?')}*",
        f"\U0001f4ca \u041e\u0431\u0449\u0430\u044f \u043e\u0446\u0435\u043d\u043a\u0430: *{result.get('total_severity', 0)}%*",
        f"\U0001f4cc \u041f\u0440\u043e\u0431\u043b\u0435\u043c \u043d\u0430\u0439\u0434\u0435\u043d\u043e: *{result.get('problems_count', 0)}*",
        f""
    ]

    problems = result.get('problems', [])
    if problems:
        lines.append("\U0001f9ec *\u041f\u0440\u043e\u0431\u043b\u0435\u043c\u044b:*")
        seen_types = set()
        for p in problems:
            if p['type'] not in seen_types:
                seen_types.add(p['type'])
                emoji_map = {
                    "acne": "\U0001f4a5",
                    "dark_circles": "\U0001f634",
                    "redness": "\U0001f534",
                    "pores": "\U0001f9c0",
                    "wrinkles": "\U0001f9cd",
                    "asymmetry": "\U0001f9a9"
                }
                e = emoji_map.get(p['type'], "\u2753")
                lines.append(f"{e} {p['type']}: {p['severity']}%")
        lines.append(f"")

    lines.append("\U0001f4a1 /start \u2014 \u043d\u043e\u0432\u044b\u0439 \u0430\u043d\u0430\u043b\u0438\u0437")
    return "\n".join(lines)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "\U0001f44b \u041f\u0440\u0438\u0432\u0435\u0442! \u042f \u0431\u043e\u0442 TruecelAnalyzer.\n\n"
        "\U0001f4f7 \u041f\u0440\u043e\u0441\u0442\u043e \u043e\u0442\u043f\u0440\u0430\u0432\u044c \u043c\u043d\u0435 \u0444\u043e\u0442\u043e \u043b\u0438\u0446\u0430 \u0430\u043d\u0444\u0430\u0441 \u2014 "
        "\u044f \u043f\u0440\u043e\u0430\u043d\u0430\u043b\u0438\u0437\u0438\u0440\u0443\u044e \u043a\u043e\u0436\u0443 \u0438 \u0434\u0430\u043c \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0430\u0446\u0438\u0438.\n\n"
        "\u0414\u043e\u043f\u0443\u0441\u0442\u0438\u043c\u044b\u0435 \u0444\u043e\u0440\u043c\u0430\u0442\u044b: PNG, JPG, WEBP"
    )


async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo and not update.message.document:
        await update.message.reply_text("\u041f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430, \u043e\u0442\u043f\u0440\u0430\u0432\u044c \u0444\u043e\u0442\u043e.")
        return

    msg = await update.message.reply_text("\U0001f504 \u0410\u043d\u0430\u043b\u0438\u0437\u0438\u0440\u0443\u044e \u043b\u0438\u0446\u043e...")

    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await photo.get_file()
            ext = ".jpg"
        else:
            doc = update.message.document
            ext = Path(doc.file_name).suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                await msg.edit_text("\u274c \u041d\u0435\u043f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u043c\u044b\u0439 \u0444\u043e\u0440\u043c\u0430\u0442. \u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439 PNG, JPG \u0438\u043b\u0438 WEBP.")
                return
            file = await doc.get_file()

        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = UPLOAD_DIR / filename
        await file.download_to_drive(filepath)

        result = analyze_face(str(filepath))
        text = format_result(result)

        if "error" not in result:
            try:
                img = cv2.imread(str(filepath))
                h, w, _ = img.shape
                for p in result.get('problem_zones', []):
                    x, y, pw, ph = p['x'], p['y'], p['w'], p['h']
                    color_map = {"acne": (255, 0, 0), "dark_circles": (100, 80, 200), "redness": (200, 0, 0),
                                  "pores": (200, 200, 0), "wrinkles": (0, 200, 200), "asymmetry": (100, 80, 220)}
                    color = color_map.get(p['type'], (200, 200, 200))
                    cv2.rectangle(img, (x, y), (x + pw, y + ph), color, 2)
                    cv2.putText(img, p['type'], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                annotated_path = UPLOAD_DIR / f"anno_{filename}"
                cv2.imwrite(str(annotated_path), img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])

                with open(annotated_path, 'rb') as f:
                    await update.message.reply_photo(photo=f, caption=text, parse_mode='Markdown')

                annotated_path.unlink(missing_ok=True)
            except Exception:
                await msg.edit_text(text, parse_mode='Markdown')
        else:
            await msg.edit_text(text, parse_mode='Markdown')

        filepath.unlink(missing_ok=True)
    except Exception as e:
        logger.exception("Bot error")
        await msg.edit_text(f"\u274c \u041e\u0448\u0438\u0431\u043a\u0430: {e}")


def main():
    if not TOKEN:
        logger.error("FACE_BOT_TOKEN not set in .env")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_photo))
    logger.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
