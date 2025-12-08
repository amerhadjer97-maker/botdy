# main.py
import os
import logging
import base64
import requests
import threading
from flask import Flask
import telebot

# ---------- إعداد السجلات ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- قراءة المتغيرات من البيئة ----------
BOT_TOKEN = os.getenv("   7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI")  # ضع اسم المتغير هذا في Render
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 10000))

if not BOT_TOKEN:
    logger.error("لم يتم العثور على TELEGRAM_BOT_TOKEN في المتغيرات البيئة. ضع توكن البوت في إعدادات Render.")
    raise SystemExit("7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI")

if not OPENAI_API_KEY:
    logger.warning("لم يتم تعيين OPENAI_API_KEY. دوال التحليل لن تعمل بدونها.")

# ---------- تهيئة البوت ----------
bot = telebot.TeleBot(BOT_TOKEN)

# ========= BOT HANDLERS =========

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 البوت شغّال بنجاح!\nارسل صورة الشارت الآن 👍")

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.reply_to(message, "📸 تم استلام الصورة! جارٍ التحليل…")
    try:
        # نحصل على ملف الصورة من تلغرام
        file_info = bot.get_file(message.photo[-1].file_id)
        file_path = file_info.file_path
        # نحمّل الصورة كـ bytes
        downloaded = bot.download_file(file_path)
        # نحفظ مؤقتاً
        tmp_path = f"/tmp/{message.photo[-1].file_id}.jpg"
        with open(tmp_path, "wb") as f:
            f.write(downloaded)

        # نستدعي دالة التحليل (تعمل فقط إذا OPENAI_API_KEY موجود)
        analysis = analyze_image(tmp_path) if OPENAI_API_KEY else "معذرة، مفتاح OpenAI غير موجود."
        bot.send_message(message.chat.id, analysis)
    except Exception as e:
        logger.exception("خطأ أثناء معالجة الصورة:")
        bot.send_message(message.chat.id, f"حدث خطأ أثناء التحليل: {e}")

# ========= دالة تحليل الصورة (مبسطة وصحيحة) =========
def analyze_image(image_path):
    """
    دالة بسيطة ترسل الصورة كمحتوى Base64 إلى نموذج المحادثة
    وتطلب تحليل وفق البرومبت العربي.
    """
    if not OPENAI_API_KEY:
        return "مفتاح OpenAI غير مضبوط."

    with open(image_path, "rb") as img:
        img_b64 = base64.b64encode(img.read()).decode()

    # نبني برومبت واحد (نص) يتضمن data URL للصورة
    prompt = (
        "أنت خبير تحليل فني محترف. حلل الشارت في الصورة المرفقة وأجب بالنقاط التالية:\n"
        "1) الاتجاه العام (صاعد/هابط/عرضي) ولماذا.\n"
        "2) نقطة دخول مقترحة وسعر تقريبي.\n"
        "3) متى يمنع الدخول (2-3 أسباب).\n"
        "4) أهداف الربح ووقف الخسارة.\n"
        "5) تحليل سريع للشموع والمؤشرات.\n\n"
        "الصورة (base64):\n"
        f"data:image/png;base64,{img_b64}\n\n"
        "أجب باللغة العربية وبنقاط واضحة."
    )

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",  # أو اختر النموذج المتوفر عندك
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 800,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        logger.error("OpenAI API error: %s %s", resp.status_code, resp.text)
        return f"فشل في الاتصال بـ OpenAI (حالة: {resp.status_code})."

    data = resp.json()
    try:
        text = data["choices"][0]["message"]["content"]
        return text
    except Exception as e:
        logger.exception("خطأ في تحليل نتيجة OpenAI:")
        return "تعذر استخراج رد من OpenAI."

# ========= FLASK SERVER =========
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

# ========= RUN BOT + SERVER =========
if __name__ == "__main__":
    def polling_thread():
        while True:
            try:
                logger.info("بدء polling للبوت...")
                bot.polling(none_stop=True, interval=0, timeout=20)
            except Exception as e:
                logger.exception("Polling failed, retrying in 5s...")
                import time
                time.sleep(5)

    thread = threading.Thread(target=polling_thread)
    thread.daemon = True
    thread.start()

    # تشغيل Flask (استخدم PORT من env)
    logger.info(f"تشغيل الويب سيرفر على المنفذ {PORT}")
    app.run(host="0.0.0.0", port=PORT)
