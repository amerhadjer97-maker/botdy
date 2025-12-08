import telebot
from transformers import pipeline
import os
from PIL import Image

# -------------------------
# 🔑 TOKEN TELEGRAM
# -------------------------

TELEGRAM_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# -------------------------
# 🧠 MODELS (مجانية)
# -------------------------

# وصف الصورة Image Caption
caption_model = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")

# كشف العناصر Object Detection
detect_model = pipeline("object-detection", model="google/owlvit-base-patch32")

# -------------------------
# 🔥 دالة التحليل PRO — مجانية
# -------------------------

def analyze_chart_free(image_path):

    # 1) وصف عام للصورة
    caption = caption_model(image_path)[0]['generated_text']

    # 2) محاولة كشف أي شيء مهم
    detected = detect_model(image_path)

    # نص مخصص حسب ما يتم إيجاده
    objects_found = [d['label'] for d in detected][:5]

    # 3) تحليل تقني مبني على الذكاء الاصطناعي البسيط
    analysis = "📊 **تحليل الشارت (نسخة مجانية):**\n\n"
    analysis += f"🖼 **وصف الصورة:** {caption}\n\n"

    # استنتاج الاتجاه من الكلمات
    if "down" in caption or "fall" in caption:
        trend = "الاتجاه العام: هابط 📉"
        suggestion = "SELL"
        reason = "الصورة تظهر شموع مائلة للأسفل مع ميل هبوطي."
    elif "up" in caption or "rise" in caption:
        trend = "الاتجاه العام: صاعد 📈"
        suggestion = "BUY"
        reason = "الصورة تظهر حركة تصاعدية واضحة."
    else:
        trend = "الاتجاه غير واضح (عرضي)."
        suggestion = "انتظار"
        reason = "لا توجد إشارة قوية."

    analysis += f"📉 {trend}\n"
    analysis += f"📍 العناصر المكتشفة: {objects_found}\n\n"
    analysis += f"💡 **أفضل صفقة مقترحة:** {suggestion}\n"
    analysis += f"🧠 **السبب:** {reason}\n"

    return analysis


# -------------------------
# 📸 استقبال الصور
# -------------------------

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "مرحبا! أرسل صورة شارت، وسأقوم بتحليلها مجاناً 🔥")


@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        image_path = "chart.jpg"
        with open(image_path, "wb") as img:
            img.write(downloaded)

        bot.reply_to(message, "⏳ جاري التحليل...")

        result = analyze_chart_free(image_path)

        bot.send_message(message.chat.id, result)

    except Exception as e:
        bot.reply_to(message, f"⚠ خطأ: {str(e)}")


# -------------------------
# 🚀 تشغيل البوت
# -------------------------

bot.polling(none_stop=True)
