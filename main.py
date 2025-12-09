import os
import telebot
from PIL import Image
import pytesseract

BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.reply_to(message,
        "🔥 أهلاً! أرسل لي أي صورة وسأقوم بتحليلها لك مباشرة.\n"
        "يدعم استخراج النصوص والتحليل الأساسي للشارتات. 📊"
    )

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        img_path = "image.jpg"
        with open(img_path, 'wb') as f:
            f.write(downloaded)

        # OCR — استخراج النص
        text = pytesseract.image_to_string(Image.open(img_path))

        if text.strip():
            bot.reply_to(message, f"📄 **النص المستخرج من الصورة:**\n{text}")
        else:
            bot.reply_to(message, "❌ لم أستطع استخراج نص من الصورة.")

    except Exception as e:
        bot.reply_to(message, "⚠️ حدث خطأ أثناء تحليل الصورة.")
        print("Error:", e)

print("🚀 البوت يعمل الآن بدون مشاكل!")
bot.infinity_polling()
