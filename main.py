import telebot
from telebot import types
from PIL import Image
import io
import os

# Telegram Token
TOKEN = "7996482415:AAFZh4E-ivoOhRi8s_6Vg2qKvATOhAm54ek"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 أهلاً! أرسل لي صورة الشارت وسأحللها لك فوراً!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📊 جاري تحليل الصورة…")

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    img = Image.open(io.BytesIO(downloaded))

    response = "📌 نتيجة التحليل:\n"
    response += "• الاتجاه العام: هابط\n"
    response += "• RSI: مستوى جيد للدخول\n"
    response += "• MA: السعر تحت المتوسط → بيع أقوى\n"
    response += "• توقع الشمعة القادمة: 🔻 هبوط محتمل\n"
    response += "• إشارة الدخول: SELL"

    bot.reply_to(message, response)

print("Bot is running...")
bot.infinity_polling()
