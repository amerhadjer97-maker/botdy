# main.py
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# اجلب التوكن من متغير بيئي (لا تضعه هنا نصاً)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not set. Please add it as an environment variable.")
    raise SystemExit("Missing BOT_TOKEN environment variable")

def analyze_chart(img_path: str) -> str:
    img = cv2.imread(img_path)
    if img is None:
        return "❌ لم أستطع قراءة الصورة."

    # OCR نصي
    try:
        text_raw = pytesseract.image_to_string(Image.open(img_path))
    except Exception:
        text_raw = ""
    text = text_raw.lower()

    result = []
    result.append("📊 **تحليل احترافي للشارت:**")

    # اتجاه تقريبي عبر حواف الصورة
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 180)
    vertical_sum = np.sum(edges, axis=0)
    mid = len(vertical_sum) // 2
    if np.sum(vertical_sum[:mid]) > np.sum(vertical_sum[mid:]):
        result.append("🔻 الترند العام: **هابط**")
        trend = "down"
    else:
        result.append("🔺 الترند العام: **صاعد**")
        trend = "up"

    # SMA موجود؟
    if "sma" in text:
        result.append("📉 مؤشر SMA موجود، احتمال وجود حركة اتجاهية قوية.")

    # بحث عن قيمة RSI في النص
    rsi_value = None
    for w in text.split():
        if w.isdigit() and 5 < int(w) < 95:
            rsi_value = int(w)
            break

    if rsi_value:
        result.append(f"📍 قيمة RSI: **{rsi_value}**")
        if rsi_value < 30:
            result.append("🔵 RSI منخفض: **منطقة تشبع بيعي → احتمال انعكاس للأعلى**")
        elif rsi_value > 70:
            result.append("🔴 RSI عالي: **تشبع شرائي → احتمال هبوط**")
        else:
            result.append("🟢 RSI طبيعي → السوق مستقر لكن يتبع الترند.")
    else:
        # بدون RSI نعتمد الترند
        if trend == "down":
            result.append("➡ القرار: **DOWN** 🔻 (اعتمادًا على الترند)")
        else:
            result.append("➡ القرار: **UP** 🔺 (اعتمادًا على الترند)")

    result.append("\n⏳ **أفضل مدة صفقة:** 1 – 3 دقائق")
    return "\n".join(result)

# handlers
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        await update.message.reply_text("أرسل صورة شارت صحيحة.")
        return

    await update.message.reply_text("⏳ جاري تحليل الشارت... 🔍")
    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_path = "chart.jpg"
    await file.download_to_drive(img_path)

    analysis = analyze_chart(img_path)
    await update.message.reply_text(analysis)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 مرحباً! أرسل صورة شارت وسأحللها لك باحتراف.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    logger.info("🔥 البوت شغال…")
    app.run_polling()

if __name__ == "__main__":
    main()
