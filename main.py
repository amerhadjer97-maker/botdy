# -*- coding: utf-8 -*-
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
import easyocr

BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

reader = easyocr.Reader(['ar', 'en'])

async def start(update, context):
    await update.message.reply_text("🔥 أرسل الصورة الآن وسأحلل النص الموجود فيها!")

async def handle_photo(update, context):
    await update.message.reply_text("⏳ جاري تحليل الصورة...")

    photo = await update.message.photo[-1].get_file()
    path = "img.jpg"
    await photo.download_to_drive(path)

    result = reader.readtext(path)
    if not result:
        await update.message.reply_text("❌ لم أستطع استخراج أي نص من الصورة.")
        return
    
    text = "\n".join([item[1] for item in result])
    await update.message.reply_text(f"📊 *النص المستخرج:*\n\n{text}", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()

if __name__ == "__main__":
    main()
