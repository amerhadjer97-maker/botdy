import cv2
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image
import os

# -------------------------------------------
# ضع التوكن هنا بين "" فقط
TELEGRAM_TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"
# -------------------------------------------


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔥 أهلاً بك! أرسل لي أي صورة شارت وسأقوم بتحليلها وإعطائك مناطق الدخول والخروج."
    )


def detect_lines_and_levels(img_gray):
    """ كشف الترندات + خطوط الدعم والمقاومة """
    edges = cv2.Canny(img_gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                            minLineLength=80, maxLineGap=10)

    levels = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # دعم / مقاومة → إذا كان الخط شبه أفقي
            if abs(y1 - y2) < 10:
                levels.append(("res_support", y1))

    return levels


def analyze_image(path):
    try:
        img = cv2.imread(path)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        levels = detect_lines_and_levels(img_gray)

        result = "📊 **نتيجة التحليل:**\n\n"

        if not levels:
            result += "لم يتم العثور على مستويات واضحة."
        else:
            for lvl_type, y in levels:
                kind = "دعم" if y > 200 else "مقاومة"
                result += f"• مستوى {kind} عند الإحداثي: {y}\n"

        # مناطق الدخول
        result += "\n🎯 **مناطق دخول مقترحة:**\n"
        if levels:
            result += "✔ الشراء فوق آخر مقاومة.\n✔ البيع تحت آخر دعم.\n"
        else:
            result += "لم تظهر مستويات دقيقة."

        return result

    except Exception as e:
        return f"خطأ أثناء التحليل: {e}"


def handle_image(update: Update, context: CallbackContext):
    file = update.message.photo[-1].get_file()
    img_path = "received.png"
    file.download(img_path)

    update.message.reply_text("⏳ جاري تحليل الصورة، انتظر قليلاً...")

    analysis = analyze_image(img_path)
    update.message.reply_text(analysis)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
