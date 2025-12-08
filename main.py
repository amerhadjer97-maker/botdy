import os
import io
import cv2
import numpy as np
import pytesseract
import pandas as pd
import pandas_ta as ta
from PIL import Image
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise RuntimeError("7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI")

def ocr_read(img_bgr):
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(img_rgb)
    text = pytesseract.image_to_string(pil, lang='eng')
    return text

def extract_candles(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 80]
    boxes = sorted(boxes, key=lambda b: b[0])[-50:]
    
    h = img_bgr.shape[0]
    candles = []
    for (x,y,w,hh) in boxes:
        price_pos = 1 - ((y + hh/2) / h)
        candles.append(price_pos)
    
    return candles

def analyze_prices(candles):
    if len(candles) < 10:
        return "الصورة غير واضحة ولا يمكن استخراج الشموع"
    
    prices = pd.Series(candles)
    df = pd.DataFrame({
        "open": prices,
        "high": prices,
        "low": prices,
        "close": prices
    })

    df["sma10"] = ta.sma(df["close"], length=10)
    df["rsi"] = ta.rsi(df["close"], length=14)

    last_close = df["close"].iloc[-1]
    last_rsi = float(df["rsi"].iloc[-1])

    if last_rsi < 30:
        signal = "BUY"
    elif last_rsi > 70:
        signal = "SELL"
    else:
        signal = "NEUTRAL"

    return f"""
📊 تحليل الشارت (مجاناً بدون OpenAI):

🔹 RSI: {last_rsi:.2f}
🔹 آخر سعر تقريبي: {last_close:.4f}

📌 الإشارة: {signal}
"""

def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    bio = io.BytesIO()
    photo.get_file().download(out=bio)
    bio.seek(0)

    img = np.array(Image.open(bio))[:, :, ::-1]

    candles = extract_candles(img)
    result = analyze_prices(candles)

    update.message.reply_text(result)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("أرسل صورة الشارت وسأحللها الآن 🔥")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
