import logging
import cv2
import numpy as np
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# التوكن الخاص بك
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"

logging.basicConfig(level=logging.INFO)

# تحليل الصورة (بدون OpenAI)
def analyze_chart(image_path):
    try:
        img = cv2.imread(image_path)

        if img is None:
            return "⚠️ لم يتم تحميل الصورة."

        # تحويل للصورة الرمادية
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # استخراج النصوص من الصورة
        text = pytesseract.image_to_string(gray)

        # تحليل بسيط للاتجاه من خلال آخر 50 بكسل
        crop = gray[:, -50:]
        avg_right = np.mean(crop)

        trend = "📈 صعود قوي" if avg_right > 120 else "📉 هبوط" if avg_right < 80 else "➡️ اتجاه جانبي"

        return f"""
📊 **تحليل الصورة (مجاني):**

🔎 الاتجاه العام: {trend}
📝 نصوص موجودة داخل الشارت:
{text}

🔥 هذا تحليل مبدئي — أرسل صورة أوضح ليعطيك نتائج أفضل!
"""
    except Exception as e:
        return f"⚠️ خطأ: {str(e)}"


def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحباً! 👋 أرسل صورة الشارت لتحليلها مجاناً 🔥")


def handle_image(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file = photo.get_file()
    image_path = "chart.jpg"
    file.download(image_path)

    result = analyze_chart(image_path)
    update.message.reply_text(result)


def main():
    updater = Updater(BOT_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
