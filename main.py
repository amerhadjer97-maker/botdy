import os
import cv2
import pytesseract
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# ---------------------------------------------------
#   🔥 TOKEN — تم وضع التوكن الخاص بك هنا مباشرة
# ---------------------------------------------------
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
# ---------------------------------------------------

# إعداد Tesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def analyze_image(image_path):
    try:
        img = cv2.imread(image_path)

        if img is None:
            return "❌ لا يمكن فتح الصورة!"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)

        if text.strip() == "":
            return "❌ لم أستطع قراءة أي نص من الصورة."

        return f"📄 النص المستخرج من الصورة:\n\n{text}"

    except Exception as e:
        return f"❌ خطأ أثناء تحليل الصورة: {str(e)}"


def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file = photo.get_file()
    image_path = "received_image.jpg"
    file.download(image_path)

    result = analyze_image(image_path)
    update.message.reply_text(result)


def start_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    print("🚀 البوت يعمل الآن…")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    start_bot()
