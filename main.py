from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# =====================
# TOKEN
# =====================
TOKEN = "7996482415:AAFhRRnmu7Fr41zkAa9OHuKntWMeqOwqRaI"

# ضع chat_id الخاص بك هنا
CHAT_ID = 123456789

# =====================
# Flask App
# =====================
app = Flask(__name__)

# =====================
# Telegram App
# =====================
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 بوت الإشارات يعمل ✅")

application.add_handler(CommandHandler("start", start))

# =====================
# Telegram Webhook
# =====================
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.process_update(update))
    loop.close()

    return "ok", 200

# =====================
# TradingView Webhook
# =====================
@app.route("/tradingview", methods=["POST"])
def tradingview_webhook():
    data = request.json

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

    application.bot.send_message(chat_id=CHAT_ID, text=message)

    return {"status": "sent"}, 200

# =====================
# Home
# =====================
@app.route("/")
def home():
    return "Bot + TradingView Webhook is running ✅"

# =====================
# Run
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
