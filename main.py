import os
import cv2
import pytesseract
import numpy as np
from PIL import Image
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ===============================
# 🔥 التوكن الخاص ببوتك (جاهز)
# ===============================
TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"

# ============= تحليل الشموع =============
def analyze_candles(prices):
    if len(prices) < 3:
        return "❌ لا توجد بيانات كافية للتحليل."

    if prices[-1] > prices[-2] > prices[-3]:
        trend = "📈 الترند صاعد"
    elif prices[-1] < prices[-2] < prices[-3]:
        trend = "📉 الترند هابط"
    else:
        trend = "➡️ الترند جانبي"

    support = min(prices)
    resistance = max(prices)
    entry = round((support + resistance) / 2, 5)

    return f"""
🔥 نتيجة التحليل:

{trend}
🟢 أقرب دعم: {support}
🔴 أقرب مقاومة: {resistance}
🎯 منطقة دخول مقترحة: {entry}

✨ التحليل يعتمد على استخراج الأسعار من الصورة وخوارزمية حركة الشموع.
"""

# ============= استخراج النص/الأرقام من الصورة =============
def extract_prices_from_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(gray)

    numbers = []
    for w in text.split():
        try:
            numbers.append(float(w.replace(",", "")))
        except:
            pass

    return numbers

# ============= تحليل الصورة =============
def analyze_image(image_path):
    prices = extract_prices_from_image(image_path)

    if len(prices) == 0:
        return "⚠️ لم أستطع استخراج الأسعار من الصورة."

    return analyze_candles(prices)

# ============= بوت تيليجرام =============
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🔥 أرسل صورة الشارت الآن وسأحللها لك!")

def handle_image(update: Update, context: CallbackContext):
    photo = update.message.photo[-1].get_file()
    image_path = "chart.jpg"
    photo.download(image_path)

    result = analyze_image(image_path)
    update.message.reply_text(result)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
