import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# -------------------------------------------
# ضع التوكن الخاص بك هنا مباشرة
# -------------------------------------------
BOT_TOKEN = "7996482415:AAHTdJmx7LIYtcXQdq-egcvq2b2hdBWuwPQ"

# -------------------------------------------
# تحليل الشارت من الصورة (نسخة مجانية بدون OpenAI)
# -------------------------------------------
def analyze_chart(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return "❌ حدث خطأ أثناء قراءة الصورة."

    # تحويل الصورة إلى رمادي
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # استخراج الحواف
    edges = cv2.Canny(gray, 50, 150)

    # حساب متوسط السطوع – يعطي فكرة عن الاتجاه العام
    brightness = np.mean(gray)

    # تقييم أولي بسيط
    if brightness > 150:
        trend = "📈 *اتجاه صاعد محتمل*"
    elif brightness < 80:
        trend = "📉 *اتجاه هابط محتمل*"
    else:
        trend = "➡️ *اتجاه جانبي*"

    return f"""
📊 **تحليل أولي للشارت:**

- السطوع المتوسط: `{brightness:.2f}`
- الاتجاه المبدئي: {trend}

⚠️ هذا تحليل تقريبي وليس تحليل دقيق.
"""

# -------------------------------------------
# استقبال الصور من المستخدم
# -------------------------------------------
def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file = photo.get_file()
    image_path = "received_image.jpg"
    file.download(image_path)

    update.message.reply_text("📥 تم استلام الصورة… يتم التحليل 🔎")

    result = analyze_chart(image_path)
    update.message.reply_text(result)

# -------------------------------------------
# أمر /start
# -------------------------------------------
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 أهلا! أرسل لي أي صورة شارت وسأقوم بتحليلها لك.")

# -------------------------------------------
# تشغيل البوت
# -------------------------------------------
def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ لم يتم العثور على التوكن!")

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    print("🤖 البوت يعمل الآن…")
    updater.idle()


if __name__ == "__main__":
    main()
