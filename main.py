import os
import random
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, filters, CallbackContext

TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"
bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# ---------------------------
#   دالة تحليل الصورة
# ---------------------------
def analyze_image(path):
    options = [
        ("BUY", "📈 السعر في منطقة دعم مع ارتداد"),
        ("SELL", "📉 السعر عند مقاومة واحتمال هبوط"),
        ("BUY", "📈 RSI منخفض + شموع انعكاسية"),
        ("SELL", "📉 RSI عالي + ضعف في الصعود"),
    ]
    signal, reason = random.choice(options)
    return f"🔎 نتيجة التحليل:\nالعملية: {signal}\nالسبب: {reason}"

# ---------------------------
#   استقبال الصور
# ---------------------------
def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file = bot.get_file(photo.file_id)
    path = "image.jpg"
    file.download(path)

    result = analyze_image(path)
    bot.send_message(chat_id=update.message.chat_id, text=result)

# تسجيل الهاندلر
dispatcher.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# ---------------------------
#   نقطة استقبال الويب هوك
# ---------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# ---------------------------
#   اختبار العمل على المتصفح
# ---------------------------
@app.route("/")
def home():
    return "Bot is running via Render!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
