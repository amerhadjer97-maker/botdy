import cv2
import pytesseract
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7996482415:AAHTdJmx7LIYtcXQdq-egcvq2b2hdBWuwPQ"

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_price(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    text = pytesseract.image_to_string(gray, config="--psm 6")
    numbers = [s.replace(" ", "") for s in text.split("\n") if "." in s]

    prices = []
    for n in numbers:
        try:
            prices.append(float(n))
        except:
            pass

    if prices:
        return max(prices), min(prices)
    return None, None

def analyze_trend(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 70, 50])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)

    red_pixels = cv2.countNonZero(mask)
    total_pixels = img.size

    ratio = red_pixels / total_pixels

    if ratio > 0.01:
        return "هابط قوي 🔻"
    elif ratio < 0.005:
        return "صاعد قوي 🔼"
    else:
        return "ترند ضعيف أو جانبي ↔️"

async def start_analysis(image_path):
    img = cv2.imread(image_path)

    last_price, low_price = extract_price(image_path)
    trend = analyze_trend(img)

    if last_price:
        decision = "UP 🔼" if trend.startswith("صاعد") else "DOWN 🔻"
    else:
        decision = "❌ لم أستطع استخراج السعر"

    msg = f"""
📊 **تحليل احترافي للشارت:**

📉 **الاتجاه:** {trend}
💲 **أعلى سعر ظاهر:** {last_price}
💲 **أقل سعر ظاهر:** {low_price}

📌 **القرار:** {decision}

⏱ **أفضل مدة للصفقة:** 1 – 3 دقائق
"""
    return msg

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    image_path = "chart.jpg"
    await photo.download_to_drive(image_path)

    msg = await start_analysis(image_path)
    await update.message.reply_text(msg)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🔥 BOT IS RUNNING...")
    await app.run_polling()

import asyncio
asyncio.run(main())
