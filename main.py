import os
import random
from flask import Flask, request
from telegram import Update
from telegram.ext import Dispatcher, MessageHandler, Filters, CommandHandler
import telegram

TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

def analyze_image():
    choices = [
        ("BUY", "📈 السعر في منطقة دعم مع ارتداد"),
        ("SELL", "📉 السعر عند مقاومة واحتمال هبوط"),
        ("BUY", "📉 RSI منخفض + شمعة انعكاس"),
        ("SELL", "📈 RSI عالي + ضعف في الزخم"),
    ]
    signal, reason = random.choice(choices)
    return f"🔎 نتيجة التحليل:\nالعملية: {signal}\nالسبب: {reason}"

def start(update, context):
    update.message.reply_text("🤖 البوت شغّال! أرسل صورة الشارت لتحليلها.")

def handle_image(update, context):
    update.message.reply_text("⏳ جاري تحليل الصورة ...")
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
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
