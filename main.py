# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import os
import telebot
from PIL import Image
import pytesseract
from flask import Flask

BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.reply_to(message, "🔥 أهلاً! أرسل لي أي صورة وسأحللها لك!")

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        msg = bot.reply_to(message, "⏳ جاري تحليل الصورة...")
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        img_path = "image.jpg"
        with open(img_path, 'wb') as f:
            f.write(downloaded)

        text = pytesseract.image_to_string(Image.open(img_path), lang='eng')
        text = text.encode('utf-8','ignore').decode('utf-8')

        if text.strip():
            bot.reply_to(message, f"📊 **النتيجة:**\n{text}")
        else:
            bot.reply_to(message, "❌ لم أستطع استخراج نص من الصورة.")

    except Exception as e:
        bot.reply_to(message, f"❌ خطأ أثناء تحليل الصورة:\n{e}")

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=lambda: bot.infinity_polling())
    t.daemon = True
    t.start()

    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
