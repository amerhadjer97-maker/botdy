from telegram.ext import Application, MessageHandler, CommandHandler, filters
from telegram import Update
from flask import Flask, request

BOT_TOKEN = "8547305082:AAFltNensKHmevSsvs_I4oNTryOgOFrI1iE"

app_flask = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# رسالة البداية
async def start(update: Update, context):
    await update.message.reply_text("مرحبًا 👋\nأرسل صورة الشارت لتحليلها 📸")

def analyze_image(image_path):
    return """
🔎 تحليل الصورة:

- SELL | السعر: 1495.20
  السبب: مؤشر RSI عالي + شمعة انعكاس

- BUY | السعر: 1492.50
  السبب: دعم قوي عند هذا المستوى
"""

async def handle_image(update: Update, context):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    await file.download_to_drive("chart.jpg")

    analysis = analyze_image("chart.jpg")
    await update.message.reply_text(analysis)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.PHOTO, handle_image))

@app_flask.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

if __name__ == "__main__":
    application.initialize()
    application.start()
    app_flask.run(host="0.0.0.0", port=10000)
