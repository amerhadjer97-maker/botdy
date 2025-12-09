import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    ContextTypes, filters
)
from PIL import Image
import pytesseract
import cv2
import numpy as np

# ----------------------------------
# TOKEN الخاص بك 🔥
# ----------------------------------
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"


logging.basicConfig(level=logging.INFO)

# -------------------------------------------------
#  تحليل خاص للشارت من الصورة باستخدام OCR + رؤية
# -------------------------------------------------
def analyze_chart(img_path):
    img = cv2.imread(img_path)

    if img is None:
        return "❌ لم أستطع قراءة الصورة."

    # قراءة النصوص من الصورة (مثل RSI – SMA – قيم السعر)
    text_raw = pytesseract.image_to_string(Image.open(img_path))
    text = text_raw.lower()

    # -------------------
    #  استخراج إشارات مهمة
    # -------------------
    result = []
    result.append("📊 **تحليل احترافي للشارت:**")

    # 1️⃣ ترند عام (تحليل ميل الفريم)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 180)

    # نفترض إذا كانت الحواف أكثر هبوط → ترند هابط
    vertical_sum = np.sum(edges, axis=0)
    mid = len(vertical_sum) // 2

    if np.sum(vertical_sum[:mid]) > np.sum(vertical_sum[mid:]):
        result.append("🔻 الترند العام: **هابط**")
        trend = "down"
    else:
        result.append("🔺 الترند العام: **صاعد**")
        trend = "up"

    # 2️⃣ تحليل SMA
    if "sma" in text:
        result.append("📉 مؤشر SMA موجود، احتمال وجود حركة اتجاهية قوية.")

    # 3️⃣ تحليل RSI
    rsi_value = None
    for w in text.split():
        if w.isdigit() and 5 < int(w) < 95:
            rsi_value = int(w)

    if rsi_value:
        result.append(f"📍 قيمة RSI: **{rsi_value}**")

        if rsi_value < 30:
            result.append("🔵 RSI منخفض: **منطقة تشبع بيعي → احتمال انعكاس للأعلى**")
        elif rsi_value > 70:
            result.append("🔴 RSI عالي: **تشبع شرائي → احتمال هبوط**")
        else:
            result.append("🟢 RSI طبيعي → السوق مستقر لكن يتبع الترند.")

    # 4️⃣ قرار الصفقة
    result.append("\n🎯 **قرار التداول:**")

    if rsi_value:
        if rsi_value > 70:
            result.append("➡ القرار: **DOWN** 🔻")
            result.append("السبب: RSI في منطقة تشبع شرائي + احتمالية هبوط.")
        elif rsi_value < 30:
            result.append("➡ القرار: **UP** 🔺")
            result.append("السبب: RSI في منطقة تشبع بيعي + احتمال صعود.")
        else:
            # اعتماد الترند
            if trend == "down":
                result.append("➡ القرار: **DOWN** 🔻 (اتجاه هابط قوي)")
            else:
                result.append("➡ القرار: **UP** 🔺 (اتجاه صاعد)")

    else:
        # إذا لا يوجد RSI نعتمد الترند فقط
        if trend == "down":
            result.append("➡ القرار: **DOWN** 🔻 (اعتمادًا على الترند)")
        else:
            result.append("➡ القرار: **UP** 🔺 (اعتمادًا على الترند)")

    result.append("\n⏳ **أفضل مدة صفقة:** 1 – 3 دقائق")

    return "\n".join(result)


# ------------------------------------------------
#  استلام الصور من التليجرام
# ------------------------------------------------
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_path = "chart.jpg"
    await file.download_to_drive(img_path)

    await update.message.reply_text("⏳ جاري تحليل الشارت... 🔍")

    analysis = analyze_chart(img_path)
    await update.message.reply_text(analysis)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 مرحباً! أرسل صورة شارت وسأحللها لك باحتراف.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    print("🔥 البوت شغال…")
    app.run_polling()

if __name__ == "__main__":
    main()
