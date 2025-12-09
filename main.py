# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import logging
import easyocr
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import Update
from telegram.ext import CallbackContext

BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"

# تفعيل اللوج
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# قارئ النصوص من الصور
reader = easyocr.Reader(['ar', 'en'])

def start(update: Update, context: CallbackContext):
    update.message.reply_text("⚡ أهلاً! أرسل لي أي صورة وسأقوم بتحليلها مباشرة.")

def analyze_image(path):
    try:
        result = reader.readtext(path, detail=1)
        text = "\n".join([item[1] for item in result])
        
        if text.strip() == "":
            return "❗ لم أستطع استخراج أي معلومات من الصورة."

        return f"📊 **تحليل الصورة:**\n\n{text}"

    except Exception as e:
        return f"❌ خطأ أثناء تحليل الصورة:\n{str(e)}"

def handle_photo(update: Update, context: CallbackContext):
    update.message.reply_text("⏳ جاري تحليل الصورة...")

    photo = update.message.photo[-1].get_file()
    path = "image.jpg"
    photo.download(path)

    analysis = analyze_image(path)

    update.message.reply_text(analysis, parse_mode="HTML")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
