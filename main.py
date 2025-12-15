import os
import random
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

TOKEN = os.environ.get("8547305082:AAFltNensKHmevSsvs_I4oNTryOgOFrI1iE")

bot = Bot(token=TOKEN)
app = Flask(__name__)

def analyze_image():
    choices = [
        ("BUY", "📈 السعر عند دعم قوي"),
        ("SELL", "📉 السعر عند مقاومة"),
        ("BUY", "📊 RSI منخفض"),
        ("SELL", "📊 RSI مرتفع"),
    ]
    signal, reason = random.choice(choices)
    return f"📊 النتيجة:\n\n🔔 العملية: {signal}\n📝 السبب: {reason}"

def start(update, context):
    update.message.reply_text("🤖 البوت شغال\n📸 أرسل صورة الشارت")

def handle_image(update, context):
    update.message.reply_text("⏳ جاري تحليل الصورة...")
    msg = analyze_image()
    update.message.reply_text(msg)

dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_image))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def home():
    return "Bot is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
