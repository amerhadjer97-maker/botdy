import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN غير موجود في Environment Variables!")

# تحليل الشارت من الصورة
def analyze_chart(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return "❌ حدث خطأ في قراءة الصورة."

    # --- استخراج جزء الشموع ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)

    # اكتشاف الاتجاه باستخدام الميل العام
    points = np.column_stack(np.where(edges > 0))
    slope = 0

    if len(points) > 50:
        x = points[:, 1]
        y = img.shape[0] - points[:, 0]
        slope, _ = np.polyfit(x, y, 1)

    trend = "📈 صاعد" if slope > 0.2 else "📉 هابط" if slope < -0.2 else "➖ عرضي"

    # --- تحليل RSI بسيط ---
    rsi_zone = "🔴 مرتفع (Overbought)" if np.mean(gray) > 150 else "🟢 منخفض (Oversold)"

    # --- القرار النهائي ---
    if trend == "📈 صاعد" and "منخفض" in rsi_zone:
        decision = "⬆️ UP (شراء)"
    elif trend == "📉 هابط" and "مرتفع" in rsi_zone:
        decision = "⬇️ DOWN (بيع)"
    else:
        decision = "⚠️ المنطقة غير مناسبة لدخول قوي"

    # --- مدة الصفقة ---
    duration = "⏳ أفضل مدة صفقة: 1 – 3 دقائق"

    result = f"""
📊 **تحليل احترافي للشارٹ**:
────────────────────

📌 **الاتجاه العام:** {trend}
📌 **حالة RSI:** {rsi_zone}
📌 **القرار:** {decision}

{duration}
"""

    return result

# استقبال الصور
def handle_photo(update: Update, context: CallbackContext):
    message = update.message
    message.reply_text("🔍 جاري تحليل الشارت… ⏳")

    photo_file = message.photo[-1].get_file()
    image_path = "chart.jpg"
    photo_file.download(image_path)

    analysis = analyze_chart(image_path)
    message.reply_text(analysis)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🔥 مرحباً! أرسل صورة شارت وسأحللها لك باحتراف.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
