import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import requests
import base64
import io
from PIL import Image

BOT_TOKEN "7996482415:AAEnb56gsGLJ-6M7NWF4efkSZFsuiCe1sZE"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------------------------
#   دالة تحليل الصور مجانا
# ---------------------------
async def analyze_image_free(image_bytes):
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    url = "https://api.chatanywhere.net/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكي تحلل الصور باحتراف شديد."},
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "حلل هذه الصورة بالتفصيل."},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{encoded}"}
                ]
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers).json()

    try:
        return response["choices"][0]["message"]["content"]
    except:
        return "⚠️ حدث خطأ أثناء التحليل."

# ---------------------------
#   استقبال الصور
# ---------------------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    image_bytes = await file.download_as_bytearray()

    await update.message.reply_text("⏳ جاري تحليل الصورة… انتظر قليلاً 🔍")

    result = await analyze_image_free(image_bytes)

    await update.message.reply_text(result)

# ---------------------------
#   استقبال النصوص
# ---------------------------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    url = "https://api.chatanywhere.net/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "أجب باحتراف وبشرح واضح."},
            {"role": "user", "content": user_text}
        ]
    }

    response = requests.post(url, json=payload, headers=headers).json()

    try:
        reply = response["choices"][0]["message"]["content"]
    except:
        reply = "⚠️ حدث خطأ."

    await update.message.reply_text(reply)

# ---------------------------
#   تشغيل البوت
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 البوت شغال! ارسل صورة أو رسالة الآن!")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
