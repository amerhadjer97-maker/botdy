import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    Filters
)

# =====================
# TOKEN من Environment
# =====================
TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Dispatcher (مهم use_context=True)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# =====================
# تحليل الصورة (تجريبي)
# =====================
def analyze_image():
    # لاحقًا ضع كود OpenCV هنا
    return "📊 النتيجة: شراء (BUY)\n💰 السعر: 1.2345\n⏱ المدة: 1 دقيقة"

# =====================
# /start
# =====================
def start(update, context):
    update.message.reply_text(
        "👋 مرحبا بك في البوت\n"
        "📸 أرسل صورة وسيتم تحليلها"
    )

# =====================
# استقبال الصور
# =====================
def handle_image(update, context):
    update.message.reply_text("⏳ جاري تحليل الصورة...")
    result = analyze_image()
    update.message.reply_text(result)

# =====================
# Handlers
# =====================
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_image))

# =====================
# Webhook
# =====================
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# =====================
# الصفحة الرئيسية
# =====================
@app.route("/")
def home():
    return "Bot is running ✅"

# =====================
# تشغيل محلي (Render يستعمل gunicorn)
# =====================
if __name__ == "__main__":
    app.run()
