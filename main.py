from flask import Flask, request
from telegram import Bot, Update
import cv2
import numpy as np
import requests
import os

TOKEN = "8566367254:AAGSL1TgX9u-5LN4EUBGdU7Tf2rcGbShKN0"
bot = Bot(token=TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅"

def analyze_chart(image_path):
    img = cv2.imread(image_path, 0)

    if img is None:
        return "❌ لم أستطع قراءة الصورة"

    # حساب الاتجاه العام (بسيط وفعال)
    h, w = img.shape
    left = np.mean(img[:, :w//3])
    right = np.mean(img[:, 2*w//3:])

    if right > left:
        return "📈 إشارة: شراء (BUY)"
    else:
        return "📉 إشارة: بيع (SELL)"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)

    # /start
    if update.message and update.message.text == "/start":
        bot.send_message(
            chat_id=update.message.chat.id,
            text=(
                "👋 مرحبا\n\n"
                "📸 أرسل صورة الشارت\n"
                "📊 وسأعطيك: شراء 📈 أو بيع 📉"
            )
        )

    # صورة
    elif update.message and update.message.photo:
        chat_id = update.message.chat.id
        file_id = update.message.photo[-1].file_id
        file = bot.get_file(file_id)

        img_url = file.file_path
        img_data = requests.get(img_url).content

        img_path = "chart.jpg"
        with open(img_path, "wb") as f:
            f.write(img_data)

        result = analyze_chart(img_path)

        bot.send_message(
            chat_id=chat_id,
            text=f"🧠 تحليل الشارت:\n{result}"
        )

        os.remove(img_path)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
