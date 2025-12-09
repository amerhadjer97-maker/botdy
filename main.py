from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image
import numpy as np
import cv2

BOT_TOKEN = "7996482415:AAHTdJmx7LIYtcXQdq-egcvq2b2hdBWuwPQ"


# ============= دوال مساعدة =============

def detect_support_resistance(gray_img):
    h, w = gray_img.shape
    horizontal_sum = np.sum(gray_img, axis=1)

    # إيجاد المناطق الأكثر تجمّعًا للبيانات (دعم/مقاومة)
    peaks = []
    threshold = np.max(horizontal_sum) * 0.65
    for i in range(1, h-1):
        if horizontal_sum[i] > threshold and horizontal_sum[i] > horizontal_sum[i-1] and horizontal_sum[i] > horizontal_sum[i+1]:
            peaks.append(i)

    if len(peaks) == 0:
        return "❌ لم يتم العثور على دعم أو مقاومة"

    support = peaks[0]
    resistance = peaks[-1]

    return support, resistance


def detect_candle_pattern(last_candle_area):
    h, w, _ = last_candle_area.shape
    top = np.mean(last_candle_area[:int(h*0.2), :, :])
    bottom = np.mean(last_candle_area[int(h*0.8):, :, :])
    center = np.mean(last_candle_area[int(h*0.4):int(h*0.6), :, :])

    if abs(top - bottom) < 10 and abs(center - bottom) < 10:
        return "➕ Doji"
    if bottom - top > 35:
        return "🔨 Hammer"
    if top - bottom > 35:
        return "📛 Shooting Star"

    return "— لا يوجد نموذج واضح"


# ============= التحليل الرئيسي =============
def analyze_chart(image_path):

    img = cv2.imread(image_path)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape

    # ========== 1) كشف الاتجاه العام ==========
    top = np.mean(gray[:int(h*0.3), :])
    bottom = np.mean(gray[int(h*0.7):, :])
    middle = np.mean(gray[int(h*0.3):int(h*0.7), :])

    if bottom < top - 20:
        trend = "📉 هابط بقوة"
    elif bottom > top + 20:
        trend = "📈 صاعد بقوة"
    else:
        trend = "➡️ اتجاه جانبي / ضعف ترند"

    # ========== 2) ميل الترند ==========
    edges = cv2.Canny(gray, 40, 150)
    ys, xs = np.where(edges > 0)

    if len(xs) > 0:
        slope = np.polyfit(xs, ys, 1)[0]
        if slope < -0.4:
            slope_text = "🔼 ميل صاعد قوي"
        elif slope < -0.2:
            slope_text = "🔼 ميل صاعد"
        elif slope > 0.4:
            slope_text = "🔽 ميل هابط قوي"
        elif slope > 0.2:
            slope_text = "🔽 ميل هابط"
        else:
            slope_text = "➡️ ميل ضعيف"
    else:
        slope_text = "❓ ميل غير واضح"

    # ========== 3) تحليل آخر شمعة ==========
    last = rgb_img[:, int(w*0.75):]

    red = np.sum((last[:,:,0] > 140) & (last[:,:,1] < 120))
    green = np.sum((last[:,:,1] > 150) & (last[:,:,0] < 120))

    if red > green:
        last_candle = "🔴 هابطة"
    else:
        last_candle = "🟢 صاعدة"

    # قوة الشمعة
    diff = abs(red - green)
    if diff > 1800:
        strength = "🔥 قوية جداً"
    elif diff > 900:
        strength = "💪 متوسطة"
    else:
        strength = "⚠️ ضعيفة"

    # ========== 4) نموذج الشمعة ==========
    candle_pattern = detect_candle_pattern(last)

    # ========== 5) دعم ومقاومة ==========
    sr = detect_support_resistance(gray)

    if isinstance(sr, tuple):
        support, resistance = sr
        sr_text = f"📉 دعم عند Y={support}\n📈 مقاومة عند Y={resistance}"
    else:
        sr_text = sr

    # ========== 6) قرار الدخول ==========
    decision = "⚠️ السوق غير واضح – تجنب الدخول"

    # UP
    if "صاعدة" in last_candle and "صاعد" in trend and "صاعد" in slope_text:
        decision = "🔥 دخول UP ممتاز"
    # DOWN
    elif "هابطة" in last_candle and "هابط" in trend and "هابط" in slope_text:
        decision = "🔻 دخول DOWN ممتاز"
    # Reversal
    if "Hammer" in candle_pattern or "Doji" in candle_pattern:
        decision = "🔄 احتمال انعكاس قوي بسبب النموذج"

    return trend, slope_text, last_candle, strength, candle_pattern, sr_text, decision


# ============= استقبال الصور =============
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    file = await update.message.photo[-1].get_file()
    img_path = "chart.jpg"
    await file.download_to_drive(img_path)

    trend, slope, candle, strength, pattern, sr, decision = analyze_chart(img_path)

    await update.message.reply_text(
        f"📊 *تحليل الشارت – النسخة ULTRA++*\n\n"
        f"🔹 الاتجاه العام: *{trend}*\n"
        f"🔹 ميل الترند: *{slope}*\n"
        f"🔹 آخر شمعة: {candle}\n"
        f"🔹 قوة الشمعة: {strength}\n"
        f"🔹 نموذج الشمعة: {pattern}\n"
        f"{sr}\n\n"
        f"🎯 *القرار النهائي:* {decision}",
        parse_mode="Markdown"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🔥 ULTRA++ AI BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
