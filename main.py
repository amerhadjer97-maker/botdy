import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pytesseract


# ================================
#  ضع التوكن الخاص بك هنا
# ================================
TELEGRAM_TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"



# ---------------------------------------------------
# دالة التحليل ULTRA
# ---------------------------------------------------
def analyze_image(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # -----------------------------
        # استخراج السعر من النقطة الزرقاء
        # -----------------------------
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        price = "غير واضح"
        try:
            text = pytesseract.image_to_string(mask, config='--psm 6')
            for t in text.split():
                if t.replace('.', '').isdigit():
                    price = t
                    break
        except:
            price = "0.0000"


        # -----------------------------
        # تحليل الترند (ZigZag)
        # -----------------------------
        zigzag_area = gray[200:800, 0:350]
        edges = cv2.Canny(zigzag_area, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, minLineLength=40, maxLineGap=5)

        trend = "غير واضح"
        if lines is not None:
            for l in lines:
                x1, y1, x2, y2 = l[0]
                if y2 < y1:
                    trend = "صاعد"
                elif y2 > y1:
                    trend = "هابط"


        # -----------------------------
        # تحليل الشموع اليمنى
        # -----------------------------
        candles = gray[:, 350:650]
        mean_color = np.mean(candles)

        if mean_color < 110:
            candle_bias = "هبوط"
        else:
            candle_bias = "صعود"


        # -----------------------------
        # قراءات RSI (تقريبية)
        # -----------------------------
        rsi_zone = gray[900:1200, :]
        rsi_value = np.mean(rsi_zone)

        if rsi_value < 90:
            rsi_signal = "في منطقة بيع قوي"
        elif rsi_value > 160:
            rsi_signal = "في منطقة شراء قوي"
        else:
            rsi_signal = "محايد"


        # -----------------------------
        # اتخاذ القرار النهائي
        # -----------------------------
        if trend == "هابط" or candle_bias == "هبوط":
            signal = "SELL ⬇️"
            reason = f"الترند {trend} – الشموع {candle_bias} – RSI {rsi_signal}"
        else:
            signal = "BUY ⬆️"
            reason = f"الترند {trend} – الشموع {candle_bias} – RSI {rsi_signal}"


        # -----------------------------
        # إخراج النتيجة
        # -----------------------------
        return f"""
🔎 نتيجة التحليل:

{signal}
📊 السعر: {price}

📌 الأسباب:
• اتجاه الترند: {trend}
• سلوك الشموع: {candle_bias}
• مؤشر RSI: {rsi_signal}
"""

    except Exception as e:
        return f"❌ خطأ أثناء التحليل: {e}"



# ---------------------------------------------------
# استقبال الصور من تيليغرام
# ---------------------------------------------------
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 أرسل لي صورة الشارت وسأحللها لك!")


def handle_image(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file = photo.get_file()
    image_path = "received_chart.jpg"
    file.download(image_path)

    update.message.reply_text("⏳ جاري تحليل الصورة…")

    result = analyze_image(image_path)
    update.message.reply_text(result)



# ---------------------------------------------------
# تشغيل البوت
# ---------------------------------------------------
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
