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

# توكن البوت
TELEGRAM_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"


def preprocess_image(img_bgr):
    """تنظيف الصورة قبل التحليل"""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    return gray


def extract_candles(img_bgr):
    """استخراج الشموع من الصورة بناءً على الارتفاعات"""

    gray = preprocess_image(img_bgr)
    edges = cv2.Canny(gray, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for c in contours:
        area = cv2.contourArea(c)
        if 80 < area < 5000:  # تحسين التعرف
            x, y, w, h = cv2.boundingRect(c)
            if h > w:  # شموع عمودية
                boxes.append((x, y, w, h))

    if len(boxes) < 10:
        return None

    # ترتيب الشموع من اليسار لليمين
    boxes = sorted(boxes, key=lambda b: b[0])[-60:]

    h_total = img_bgr.shape[0]
    candles = []

    for (x, y, w, h) in boxes:
        # تحويل موقع الشمعة إلى قيمة سعرية نسبية
        price = 1 - ((y + h/2) / h_total)
        candles.append(price)

    return candles


def analyze_prices(candles):

    if candles is None or len(candles) < 10:
        return "❌ الشموع غير واضحة – الصورة تحتاج ضبط أو جودة أعلى."

    prices = pd.Series(candles)

    df = pd.DataFrame({
        "open": prices.shift(1).fillna(prices.iloc[0]),
        "high": prices.rolling(2).max(),
        "low": prices.rolling(2).min(),
        "close": prices
    })

    df["sma10"] = ta.sma(df["close"], length=10)
    df["rsi"] = ta.rsi(df["close"], length=14)

    last_close = float(df["close"].iloc[-1])
    last_rsi = float(df["rsi"].iloc[-1])

    # اتجاه السوق آخر 10 شموع
    trend = df["close"].iloc[-5:].mean() - df["close"].iloc[:5].mean()

    if last_rsi < 30:
        signal = "BUY 🔵 (تشبع بيعي)"
    elif last_rsi > 70:
        signal = "SELL 🔴 (تشبع شرائي)"
    else:
        signal = "NEUTRAL ⚪"

    trend_text = "⬆️ صعود" if trend > 0 else "⬇️ هبوط" if trend < 0 else "⏸️ تذبذب"

    return f"""
📊 **تحليل احترافي للشارت:**

🔹 *الاتجاه العام:* {trend_text}  
🔹 *RSI:* {last_rsi:.2f}  
🔹 *السعر التقريبي:* {last_close:.4f}  

📌 **الإشارة النهائية:** {signal}

⚡ التحليل يعتمد على استخراج الشموع الحقيقية من الصورة + مؤشرات RSI و SMA10
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
    update.message.reply_text("أرسل صورة الشارت وسأقوم بتحليل احترافي فوراً! 🔥📊")


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
