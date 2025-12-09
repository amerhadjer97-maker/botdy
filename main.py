import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import requests

BOT_TOKEN = "7996482415:AAHTdJmx7LIYtcXQdq-egcvq2b2hdBWuwPQ"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# تحليل الصورة (نسخة مجانية — بدون OpenAI)
def analyze_image_local(image_path):
    return "✅ تم استلام الصورة! (نسخة مجانية لذلك التحليل محدود) \n\nأرسل لي صورة أخرى!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 البوت شغال! أرسل صورة الآن!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "image.jpg"
    await file.download_to_drive(file_path)

    result = analyze_image_local(file_path)
    await update.message.reply_text(result)

def main():
    print("🔥 BOT IS RUNNING...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # VERY IMPORTANT: no asyncio.run()!!
    app.run_polling()

if __name__ == "__main__":
    main()
