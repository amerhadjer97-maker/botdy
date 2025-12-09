import cv2
import numpy as np
import pytesseract
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext
from telegram import Update

# ✔️ تم وضع التوكن الخاص بك هنا مباشرة
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"

def analyze_chart(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return "❌ لم أستطع قراءة الصورة!"

    # -------- تحليل الاتجاه --------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=80, maxLineGap=10)

    trend = "غير واضح"
    if lines is not None:
        slopes = []
        for x1, y1, x2, y2 in lines[:, 0]:
            if x2 - x1 != 0:
                slopes.append((y2 - y1) / (x2 - x1))

        if len(slopes) > 0:
            avg_slope = np.mean(slopes)
            if avg_slope < -0.2:
                trend = "⬇️ ترند هابط قوي"
            elif avg_slope > 0.2:
                trend = "⬆️ ترند صاعد"
            else:
                trend = "➡️ ترند جانبي"

    # -------- قراءة النصوص --------
    text = pytesseract.image_to_string(gray, lang="eng")

    result = f"""
📊 **تحليل الشارت**

📉 الاتجاه: {trend}

🔍 النص الموجود:
{text}

🔥 هذا تحليل مجاني تماماً بدون OpenAI
"""
    return result


def start(update: Update, context: CallbackContext):
    update.message.reply_text("أرسل صورة الشارت الآن وسأحللها مباشرة 🔥📈")


def handle_image(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file = context.bot.get_file(photo.file_id)
    file_path = "chart.jpg"
    file.download(file_path)

    result = analyze_chart(file_path)
    update.message.reply_text(result)


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
