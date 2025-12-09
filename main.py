from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image
import numpy as np

BOT_TOKEN = "7996482415:AAHTdJmx7LIYtcXQdq-egcvq2b2hdBWuwPQ"


# ============= التحليل المتطوّر بدون OpenAI =============
def ultra_analyze(image_path):

    img = Image.open(image_path).convert("RGB")
    np_img = np.array(img)

    h, w, _ = np_img.shape

    # ---------- تحليل آخر شمعة ----------
    right = np_img[:, int(w * 0.78): w]

    red_px = np.sum((right[:, :, 0] > 180) & (right[:, :, 1] < 120))
    green_px = np.sum((right[:, :, 1] > 150) & (right[:, :, 0] < 130))

    if red_px > green_px:
        last_candle = "🔴 هابطة"
    else:
        last_candle = "🟢 صاعدة"

    # ---------- اتجاه السعر ----------
    top = np.mean(np_img[:int(h * 0.3), :, 1])
    mid = np.mean(np_img[int(h * 0.4):int(h * 0.6), :, 1])
    bottom = np.mean(np_img[int(h * 0.7):, :, 1])

    if bottom < mid < top:
        trend = "📉 هابط بقوة"
    elif bottom > mid > top:
        trend = "📈 صاعد بقوة"
    else:
        trend = "➡️ اتجاه جانبي"

    # ---------- تقدير الدعم والمقاومة ----------
    low_zone = np.mean(np_img[int(h * 0.75):, :, 2])
    high_zone = np.mean(np_img[:int(h * 0.25), :, 2])

    if low_zone < 90:
        support = "🟦 دعم قوي"
    else:
        support = "▪ دعم ضعيف"

    if high_zone < 90:
        resistance = "🟥 مقاومة قوية"
    else:
        resistance = "▪ مقاومة ضعيفة"

    # ---------- قرار الدخول ----------
    if trend.startswith("📈") and last_candle == "🟢 صاعدة":
        decision = "🔥 فرصة UP ممتازة"
    elif trend.startswith("📉") and last_candle == "🔴 هابطة":
        decision = "🔻 فرصة DOWN قوية"
    else:
        decision = "⚠️ السوق غير مناسب"

    return trend, last_candle, support, resistance, decision


# ============= استقبال وتحليل الصور =============
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]
    file = await photo.get_file()

    img_path = "chart.jpg"
    await file.download_to_drive(img_path)

    trend, candle, support, resistance, decision = ultra_analyze(img_path)

    await update.message.reply_text(
        f"📊 *ULTRA FREE – التحليل المتقدّم*\n\n"
        f"🔹 الاتجاه: *{trend}*\n"
        f"🔹 آخر شمعة: {candle}\n"
        f"🔹 {support}\n"
        f"🔹 {resistance}\n\n"
        f"🎯 *القرار*: {decision}",
        parse_mode="Markdown"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🔥 ULTRA FREE BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
