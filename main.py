from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image
import numpy as np

BOT_TOKEN = "7996482415:AAHTdJmx7LIYtcXQdq-egcvq2b2hdBWuwPQ"


# ============= تحليل الشارت بدون OpenAI =============
def analyze_chart(image_path):

    img = Image.open(image_path).convert("RGB")
    np_img = np.array(img)

    h, w, _ = np_img.shape

    # ----- تحليل آخر شمعة -----
    right_area = np_img[:, int(w*0.75):w]

    red_px = np.sum((right_area[:,:,0] > 180) & (right_area[:,:,1] < 100))
    green_px = np.sum((right_area[:,:,1] > 150) & (right_area[:,:,0] < 120))

    if red_px > green_px:
        last_candle = "🔴 هابطة"
    else:
        last_candle = "🟢 صاعدة"

    # ----- تقدير الاتجاه -----
    top = np.mean(np_img[:int(h*0.3), :, 1])
    bottom = np.mean(np_img[int(h*0.7):, :, 1])

    if bottom < top - 15:
        trend = "📉 اتجاه هابط"
    elif bottom > top + 15:
        trend = "📈 اتجاه صاعد"
    else:
        trend = "➡️ اتجاه جانبي"

    # ----- قرار دخول تقريبي -----
    if last_candle == "🟢 صاعدة" and trend == "📈 اتجاه صاعد":
        decision = "🔥 دخول UP محتمل"
    elif last_candle == "🔴 هابطة" and trend == "📉 اتجاه هابط":
        decision = "🔻 دخول DOWN محتمل"
    else:
        decision = "⚠️ لا يوجد دخول مؤكّد"

    return trend, last_candle, decision


# ============= استقبال الصور =============
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]
    file = await photo.get_file()

    img_path = "chart.jpg"
    await file.download_to_drive(img_path)

    trend, candle, decision = analyze_chart(img_path)

    await update.message.reply_text(
        f"📊 *تحليل الشارت – النسخة المجانية*\n\n"
        f"🔹 الاتجاه: *{trend}*\n"
        f"🔹 آخر شمعة: {candle}\n\n"
        f"🎯 *القرار:* {decision}",
        parse_mode="Markdown"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🔥 FREE BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
