import telebot
from transformers import pipeline
from PIL import Image
import os

# ===========================
# 🔑 توكن تيليجرام
# ===========================

TELEGRAM_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ===========================
# 📥 تحميل نماذج مجانية (رسمياً من HuggingFace)
# ===========================

caption_model = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
object_model = pipeline("object-detection", model="google/owlvit-base-patch32")

# ===========================
# 🔥 دالة التحليل المجاني
# ===========================

def analyze_chart(image_path):

    # 1) وصف للصورة
    caption = caption_model(image_path)[0]['generated_text']

    # 2) كشف العناصر (شموع – خطوط – نصوص…)
    detected = object_model(image_path)
    objects = [d['label'] for d in detected]

    # 3) تحليل ذكي بسيط
    analysis = "📊 **تحليل الشارت (نسخة مجانية)**\n\n"
    analysis += f"🖼 **وصف الصورة:** {caption}\n\n"

    # استنتاج اتجاه محتمل
    if "up" in caption or "rise" in caption or "bull" in caption:
        direction = "🔼 الاتجاه: صاعد"
        signal = "BUY"
        reason = "الصورة تظهر حركات صاعدة أو شمعة قوية للأعلى."
    elif "down" in caption or "fall" in caption or "bear" in caption:
        direction = "🔽 الاتجاه: هابط"
        signal = "SELL"
        reason = "الصورة تظهر حركة هبوطية أو شموع حمراء."
    else:
        direction = "➡ الاتجاه: عرضي"
        signal = "انتظار"
        reason = "لا توجد إشارة واضحة."

    analysis += f"{direction}\n"
    analysis += f"📌 العناصر المكتشفة: {objects[:5]}\n\n"
    analysis += f"💡 **الإشارة المقترحة:** {signal}\n"
    analysis += f"🧠 **السبب:** {reason}\n"

    return analysis

# ===========================
# 📸 استقبال الصور
# ===========================

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(m, "🔥 مرحباً! أرسل صورة الشارت وسأحللها مجاناً!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        image_path = "chart.jpg"
        with open(image_path, "wb") as f:
            f.write(downloaded)

        bot.reply_to(message, "⏳ جاري تحليل الصورة...")

        result = analyze_chart(image_path)
        bot.send_message(message.chat.id, result)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠ خطأ: {str(e)}")

# ===========================
# 🚀 تشغيل البوت
# ===========================

bot.polling(none_stop=True)
