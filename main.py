   import asyncio
from flask import Flask, request

from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =====================
# TOKEN (مباشر)
# =====================
BOT_TOKEN = "7996482415:AAFhRRnmu7Fr41zkAa9OHuKntWMeqOwqRaI"

# =====================
# Flask App
# =====================
app = Flask(__name__)

# =====================
# Telegram App
# =====================
application = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(token=BOT_TOKEN)

# =====================
# /start
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبا بك\n"
        "📊 هذا بوت إشارات TradingView\n"
        "⏳ في انتظار الإشارات..."
    )

# =====================
# Handlers
# =====================
application.add_handler(CommandHandler("start", start))

# =====================
# Telegram Webhook
# =====================
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "ok", 200

# =====================
# TradingView Webhook
# =====================
@app.route("/tradingview", methods=["POST"])
def tradingview_webhook():
    data = request.json

    # مثال رسالة من TradingView
    symbol = data.get("symbol", "UNKNOWN")
    signal = data.get("signal", "NO SIGNAL")
    price = data.get("price", "N/A")
    timeframe = data.get("timeframe", "N/A")

    message = (
        "📊 إشارة TradingView\n\n"
        f"📌 الزوج: {symbol}\n"
        f"📈 الإشارة: {signal}\n"
        f"💰 السعر: {price}\n"
        f"⏱ الفريم: {timeframe}"
    )

    # أرسل الرسالة (ضع chat_id الخاص بك)
    bot.send_message(
        chat_id=YOUR_CHAT_ID,
        text=message
    )

    return {"status": "sent"}, 200

# =====================
# Home
# =====================
@app.route("/")
def home():
    return "Bot is running ✅"

# =====================
# Run
# =====================
if __name__ == "__main__":
    application.initialize()
    application.start()
    app.run(host="0.0.0.0", port=10000)
