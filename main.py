import cv2
import numpy as np
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ======================
# 🔥 تم وضع التوكن هنا
# ======================
BOT_TOKEN = "7996482415:AAHTdJmx7LIYtcXQdq-egcvq2b2hdBWuwPQ"


# ========== دالة تحليل الصورة ==========
def analyze_chart(image_path):
    img = cv2.imread(image_path)

    # OCR استخراج النصوص
    text = pytesseract.image_to_string(Image.open(image_path))

    # --- التقاط RSI ---
    import re
    rsi_value = None
    match = re.search(r"RSI.*?(\d{2})", text)
    if match:
        rsi_value = int(match.group(1))

    # --- استخراج الاتجاه ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 40, 150)

    ys, xs = np.where(edges > 0)
    trend = "غير واضح"
    if len(xs) > 10:
        coef = np.polyfit(xs, ys, 1)[0]
        if coef < -0.25:
            trend = "📈 صاعد"
        elif coef > 0.25:
            trend = "📉 هابط"
        else:
            trend = "➡️ جانبي"

    # --- استخراج لون آخر 3 شموع ---
    last_candles = []
    height, width = img.shape[:2]
    candle_area = img[int(height*0.2):int(height*0.8), int(width*0.7):width]

    hsv = cv2.cvtColor(candle_area, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv, (0,50,50), (10,255,255))
    mask_green = cv2.inRange(hsv, (40,50,50), (90,255,255))

    red_pixels = np.sum(mask_red > 0)
    green_pixels = np.sum(mask_green > 0)

    last_candle = "🔴 هابطة" if red_pixels > green_pixels else "🟢 صاعدة"

    # --- قرار الدخول ---
    decision = "⚠️ لا يوجد دخول مؤكّد"
    reason = ""

    if rsi_value:
        if rsi_value < 30:
            decision = "🔥 دخول UP"
            reason += f"• RSI ({rsi_value}) في تشبع بيع\n"
        elif rsi_value > 70:
            decision = "🔻 دخول DOWN"
            reason += f"• RSI ({rsi_value}) في تشبع شراء\n"

    if "صاعد" in trend:
        reason += "• الاتجاه العام صاعد\n"
    elif "هابط" in trend:
        reason += "• الاتجاه العام هابط\n"

    reason += f"• آخر شمعة: {last_candle}\n"

    return trend, rsi_value, last_candle, decision, reason


# ========== عند استلام صورة ==========
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()

    img_path = "chart.jpg"
    await file.download_to_drive(img_path)

    trend, rsi, candle, decision, reason = analyze_chart(img_path)

    await update.message.reply_text(
        f"📊 **تحليل الشارت – النسخة ULTRA**\n\n"
        f"🔹 الاتجاه: **{trend}**\n"
        f"🔹 RSI: **{rsi if rsi else 'غير موجود'}**\n"
        f"🔹 آخر شمعة: {candle}\n\n"
        f"🧠 **أسباب القرار:**\n{reason}\n"
        f"🎯 **القرار النهائي:** {decision}"
    )


# ========== تشغيل البوت ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🚀 Bot Started Running (ULTRA MODE)")
    app.run_polling()


if __name__ == "__main__":
    main()
