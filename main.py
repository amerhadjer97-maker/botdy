import cv2
import numpy as np
from telegram.ext import Updater, MessageHandler, Filters
import telegram
import os

# ---------------------------
# التوكن الخاص ببوتك
# ---------------------------
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"

# ---------------------------
# تحليل احترافي للصورة
# ---------------------------
def analyze_chart(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return "❌ لم أستطع قراءة الصورة!"

    # 1 — كشف الاتجاه العام (Trend)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 60, 180)

    # حساب ميل الاتجاه تقريبي
    ys, xs = np.where(edges > 0)
    if len(xs) == 0:
        trend_text = "غير واضح"
    else:
        coef = np.polyfit(xs, ys, 1)[0]
        if coef < -0.2:
            trend_text = "📈 ترند صاعد"
        elif coef > 0.2:
            trend_text = "📉 ترند هابط"
        else:
            trend_text = "➡ ترند جانبي"

    # 2 — التعرف على لون الشموع (أخضر/أحمر)
    h, w = img.shape[:2]
    center = img[int(h * 0.68):int(h * 0.88), int(w * 0.1):int(w * 0.9)]
    avg_color = center.mean(axis=(0, 1))
    r, g, b = avg_color

    if g > r:
        candle = "🟢 شموع صاعدة"
        bias = "BUY"
    else:
        candle = "🔴 شموع هابطة"
        bias = "SELL"

    # 3 — دعم / مقاومة تقريبية عبر مستوى اللون
    bottom_strip = gray[int(h * 0.8):int(h * 0.95), :]
    avg_light = bottom_strip.mean()

    if avg_light < 110:
        level = "📉 مستوى دعم قريب – احتمال ارتداد"
    else:
        level = "📈 مستوى مقاومة – احتمال انعكاس"

    # 4 — تحليل RSI تقريبي (من خط أسفل الرسم)
    rsi_zone = img[int(h * 0.9):h, :]
    rsi_gray = cv2.cvtColor(rsi_zone, cv2.COLOR_BGR2GRAY)
    rsi_level = rsi_gray.mean()

    if rsi_level < 90:
        rsi_text = "🔵 RSI منخفض — منطقة BUY"
    elif rsi_level > 150:
        rsi_text = "🔴 RSI مرتفع — منطقة SELL"
    else:
        rsi_text = "🟡 RSI متوسط — لا يوجد تشبع"

    # القرار النهائي
    if bias == "BUY" and "دعم" in level:
        decision = "🔥 دخول BUY ممتاز"
        price_suggest = "⬆ السعر: منطقة ارتداد قوية"
    elif bias == "SELL" and "مقاومة" in level:
        decision = "🔥 دخول SELL ممتاز"
        price_suggest = "⬇ السعر: عند مقاومة واضحة"
    else:
        decision = "⚠ دخول غير مثالي – انتظر تأكيد"
        price_suggest = "❗ السعر غير واضح"

    # النتيجة النهائية
    result = f"""
📊 **تحليل احترافي للصورة**

**🔹 الاتجاه:** {trend_text}
**🔹 الشموع:** {candle}
**🔹 المنطقة:** {level}
**🔹 مؤشر RSI:** {rsi_text}

———————————

🎯 **التوصية:** {decision}
💰 **المستوى المقترح:** {price_suggest}

⚡ تحليل مبني على قراءة الصورة فقط – بدون ذكاء اصطناعي خارجي.
"""

    return result


# ---------------------------
# استقبال الصور من المستخدم
# ---------------------------
def handle_image(update, context):
    file = update.message.photo[-1].get_file()
    file_path = "chart.jpg"
    file.download(file_path)

    analysis = analyze_chart(file_path)

    update.message.reply_text(analysis, parse_mode="Markdown")


# ---------------------------
# تشغيل البوت
# ---------------------------
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
