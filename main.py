from flask import Flask, request
import os
import telegram
from telegram import Update
from telegram.ext import Dispatcher, MessageHandler, Filters, CommandHandler

TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

# ---------------------------
# 🔥 التحليل الجاهز
# ---------------------------
def generate_fake_analysis():
    return (
        "🔎 تحليل الصورة:\n"
        "- SELL | السعر: 1495.20\n"
        "  السبب: مؤشر RSI عالي + شمعة انعكاس\n\n"
        "- BUY | السعر: 1492.50\n"
        "  السبب: دعم قوي عند هذا المستوى\n"
    )

# ---------------------------
# الهاندلرز
# ---------------------------
def start(update, context):
    update.message.reply_text("👋 أهلاً! أرسل صورة وسأحللها لك فوراً.")

def handle_image(update, context):
    update.message.reply_text("⏳ جارٍ تحليل الصورة...")
    analysis = generate_fake_analysis()
    update.message.reply_text(analysis)

# ---------------------------
# Dispatcher صحيح 100%
# ---------------------------
dispatcher = Dispatcher(bot, update_queue=None, workers=4, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_image))

# ---------------------------
# Webhook endpoint
# ---------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def home():
    return "Bot is running!"

# ---------------------------
# تشغيل السيرفر على Render
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
