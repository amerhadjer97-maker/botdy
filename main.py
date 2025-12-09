# -*- coding: utf-8 -*-
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import telebot
import cv2
import numpy as np

BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 أهلاً! أرسل لي أي صورة شارت وسأحللها لك الآن!")

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    bot.reply_to(message, "⏳ جاري تحليل الصورة...")

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        img_path = "chart.jpg"
        with open(img_path, 'wb') as new_file:
            new_file.write(downloaded)

        img = cv2.imread(img_path)

        if img is None:
            raise Exception("الصورة غير صالحة")

        # تحليل بسيط: استخراج الاتجاه العام من الصورة
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        avg_intensity = np.mean(edges)

        if avg_intensity > 30:
            trend = "📉 الاتجاه غالباً هابط"
        else:
            trend = "📈 الاتجاه غالباً صاعد"

        bot.reply_to(message, f"📊 **النتيجة:**\n{trend}")

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء تحليل الصورة:\n{e}")

bot.infinity_polling()
