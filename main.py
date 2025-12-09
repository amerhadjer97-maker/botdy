import logging
import easyocr
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction
import cv2
import numpy as np
from PIL import Image
import io

# -----------------------------
# وضع التوكن هنا
BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"
# -----------------------------

logging.basicConfig(level=logging.INFO)
reader = easyocr.Reader(['en'])  # لغة قراءة النصوص

def start(update, context):
    update.message.reply_text("🚀 البوت شغال! أرسل صورة وسأحللها فوراً.")

def analyze_image_bytes(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    result = reader.readtext(img)

    text_result = "\n".join([res[1] for res in result]) if result else "❌ لا يوجد نص واضح في الصورة"
    return text_result

def handle_photo(update, context):
    update.message.chat.send_action(ChatAction.TYPING)

    photo_file = update.message.photo[-1].get_file()
    image_bytes = photo_file.download_as_bytearray()

    text = analyze_image_bytes(image_bytes)
    update.message.reply_text("🔍 *تحليل الصورة:*\n\n" + text)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
