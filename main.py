import os
import io
import cv2
import numpy as np
from PIL import Image
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# -----------------------------
#  التوكن الخاص بك (ملصوق هنا)
# -----------------------------
TELEGRAM_TOKEN = "7996482415:AAEnb56gsGLJ-6M7NWF4efkSZFsuiCe1sZE"

# دالة تحليل الصورة (تحليل بسيط + استخراج مناطق مهمة)
def analyze_chart_image(img_path):
    try:
        # قراءة الصورة
        img = cv2.imread(img_path)

        if img is None:
            return "❌ لم أستطع قراءة الصورة"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # فلترة لتحسين الشموع
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # اكتشاف الحواف لتحليل الاتجاه
        edges = cv2.Canny(blur, 50, 150)

        # حساب متوسط الحواف لمعرفة الترند
        strength = np.mean(edges)

        if strength > 60:
            trend = "📈 ترند صاعد"
        else:
            trend = "📉 ترند هابط"

        # تحديد مناطق دخول تقديرية (بسيطة)
        h, w = gray.shape
        entry_zone_buy = f"منطقة شراء تقريبية: تحت السعر بـ {(h//12)}"
        entry_zone_sell = f"منطقة بيع تقريبية: فوق السعر بـ {(h//10)}"

        return f"""
✅ *تم تحليل الصورة بنجاح*

🔍 *الترند الحالي:* {trend}

🎯 *مناطق الدخول:*
- {entry_zone_buy}
- {entry_zone_sell}

⚙️ التحليل تجريبي — يمكن تطويره أكثر إذا تريد.
"""
    except Exception as e:
        return f"حدث خطأ: {str(e)}"


# استقبال الصور
def handle_photo(update: Update, context: CallbackContext):
    try:
        file = update.message.photo[-1].get_file()
        img_path = "received.jpg"
        file.download(img_path)

        result = analyze_chart_image(img_path)
        update.message.reply_text(result, parse_mode="Markdown")

    except Exception as e:
        update.message.reply_text("❌ خطأ أثناء معالجة الصورة: " + str(e))


def start(update: Update, context: CallbackContext):
    update.message.reply_text("🔥 أرسل لي أي صورة شارت وسأحللها لك فوراً!")


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
