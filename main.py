# -*- coding: utf-8 -*-
import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext
from telegram import Update
import easyocr
import os

BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# OCR Reader (ننشئه مرة واحدة فقط لتسريع الأداء)
reader = easyocr.Reader(['ar', 'en'], gpu=False)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🔥📸 أهلاً! أرسل أي صورة وسأقوم بتحليل النص الموجود داخلها فوراً!")

def analyze_image(path):
    try:
        result = reader.readtext(path)

        if not result:
            return "❌ لم أستطع استخراج أي نص من الصورة."

        text = "\n".join([item[1] for item in result])
        return f"📊 *تحليل الصورة:* \n\n{text}"

    except Exception as e:
        return f"❌ خطأ أثناء التحليل:\n{str(e)}"

def handle_photo(update: Update, context: CallbackContext):
    update.message.reply_text("⏳ جاري تحليل الصورة...")

    file = update.message.photo[-1].get_file()
    path = "image.jpg"
    file.download(path)

    response = analyze_image(path)
    update.message.reply_text(response, parse_mode="Markdown")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    logging.info("🚀 البوت يعمل الآن بدون API!")

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
