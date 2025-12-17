import asyncio
from flask import Flask, request

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =====================
# TOKEN (مباشرة)
# =====================
TOKEN = "7996482415:AAFhRRnmu7Fr41zkAa9OHuKntWMeqOwqRaI"

# =====================
# Flask App
# =====================
app = Flask(__name__)

# =====================
# Telegram Application
# =====================
application = ApplicationBuilder().token(TOKEN).build()

# =====================
# تحليل الصورة (تجريبي)
# =====================
def analyze_image():
    return (
        "📊 النتيجة: شراء (BUY)\n"
        "💰 السعر: 1.2345\n"
        "⏱ المدة: 1 دقيقة"
    )

# =====================
# /start
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبا بك في البوت\n"
        "📸 أرسل صورة وسيتم تحليلها"
    )

# =====================
# استقبال الصور
# =====================
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري تحليل الصورة...")
    result = analyze_image()
    await update.message.reply_text(result)

# =====================
# Handlers
# =====================
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.PHOTO, handle_image))

# =====================
# Webhook
# =====================
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)

    asyncio.run(application.process_update(update))

    return "ok", 200

# =====================
# الصفحة الرئيسية
# =====================
@app.route("/")
def home():
    return "Bot is running ✅"
