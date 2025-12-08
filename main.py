import os
import io
import cv2
import numpy as np
import pytesseract
import pandas as pd
import pandas_ta as ta
from PIL import Image
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# === CONFIG ===
# لا تضع التوكن هنا مباشرة. في بيئة التطوير:
# export TELEGRAM_TOKEN="ضع_توكن_البوت_هنا"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("ضع TELEGRAM_TOKEN في متغيرات البيئة قبل التشغيل.")

# === HELPER: استخراج نص من الصورة ===
def ocr_read(img_bgr):
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(img_rgb)
    text = pytesseract.image_to_string(pil, lang='eng+ara')  # قم بتعديل اللغات حسب الحاجة
    return text

# === HELPER: كشف شمعات تقريبي ===
def extract_candles_from_image(img_bgr, n_candles=50):
    # تحويل إلى رمادي وتهيئة
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # تخفيف الضوضاء
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    # ثنائية
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # عكس إن كان الشارت داكن الخلفية فاتحة، اضبط هذه الخطوات بحسب شكل الشارت
    # البحث عن contours طويلة (تقديري)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # نأخذ bounding boxes كبيرة أفقياً (تمثل شمعات)
    boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 50]
    # فرز حسب x وتحجيم
    boxes = sorted(boxes, key=lambda b: b[0])
    # نأخذ آخر n_candles أو جميعها
    boxes = boxes[-n_candles:]
    # نحول كل مربع لقيمة سعرية تقريبية: نستخدم موضع y كقيمة نسبية
    h = img_bgr.shape[0]
    candles = []
    for (x,y,w,hh) in boxes:
        # مركز عمودي للمربع كـ "سعر" تقديري
        center_y = y + hh/2
        rel = 1 - (center_y / h)  # 0..1 (أعلى = اقرب للقيمة العليا)
        candles.append({'x': x, 'y': y, 'w': w, 'h': hh, 'rel_price': rel})
    return candles

# === بناء سلسلة سعر تقريبي ===
def build_price_series(candles):
    # نرتب ونحول rel_price لسعر افتراضي (سنقوم بتطبيع لاحقًا)
    candles = sorted(candles, key=lambda c: c['x'])
    rels = [c['rel_price'] for c in candles]
    # افتراض سعر نطاق مثلاً 100..200 (سيتم تعديل هذا بالـ OCR لقراءة الأرقام)
    if not rels:
        return None
    prices = [100 + r * 100 for r in rels]  # dummy scale
    df = pd.DataFrame({
        'open': prices, 'high': prices, 'low': prices, 'close': prices
    })
    return df

# === تحليل تقني بسيط ===
def analyze_price_df(df):
    out = {}
    df['sma10'] = ta.sma(df['close'], length=10)
    df['rsi'] = ta.rsi(df['close'], length=14)
    last_rsi = df['rsi'].iloc[-1] if 'rsi' in df else None
    last_close = df['close'].iloc[-1]
    last_sma = df['sma10'].iloc[-1]
    # قواعد بسيطة
    if last_rsi is not None:
        if last_rsi < 30 and last_close > last_sma:
            out['signal'] = 'BUY'
        elif last_rsi > 70 and last_close < last_sma:
            out['signal'] = 'SELL'
        else:
            out['signal'] = 'NEUTRAL'
    else:
        out['signal'] = 'NEUTRAL'
    out['last_rsi'] = float(last_rsi) if last_rsi is not None else None
    out['last_close'] = float(last_close)
    return out

# === معالجة الصورة الواردة من تيليجرام ===
def handle_image(update: Update, context: CallbackContext):
    msg = update.message
    photo = msg.photo[-1]  # أفضل جودة
    bio = io.BytesIO()
    photo.get_file().download(out=bio)
    bio.seek(0)
    pil = Image.open(bio).convert("RGB")
    img = np.array(pil)[:, :, ::-1]  # PIL RGB -> OpenCV BGR

    # OCR (محاول قراءة محاور السعر)
    text = ocr_read(img)

    # استخراج شمعات تقريبي
    candles = extract_candles_from_image(img, n_candles=60)
    df = build_price_series(candles)
    if df is None:
        update.message.reply_text("لم أتمكن من استخراج بيانات كافية من الصورة. جرّب صورة أو جودة مختلفة.")
        return

    analysis = analyze_price_df(df)
    reply = f"تحليل صورة (تقديري):\nالاشارة: {analysis['signal']}\nآخر RSI تقريبي: {analysis.get('last_rsi')}\n(هذا تحليل تقريبي جداً — اضبط المعالجة حسب شكل الشارت)"
    update.message.reply_text(reply)

# === أوامر بوت بسيطة ===
def start(update: Update, context: CallbackContext):
    update.message.reply_text("أرسل صورة الشارت وسأحاول تحليلها (نسخة مجانية ومبدئية).")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    updater.start_polling()
    print("Bot started")
    updater.idle()

if __name__ == "__main__":
    main()
