import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"

# --- دالة تحليل الصورة ---
def analyze_image(path):
    # تحليل تجريبي يعتمد على random (للتجربة فقط)
    options = [
        ("BUY", "📈 السعر في منطقة دعم مع ارتداد"),
        ("SELL", "📉 السعر عند مقاومة واحتمال هبوط"),
        ("BUY", "📈 RSI منخفض + شموع انعكاسية"),
        ("SELL", "📉 RSI عالي + ضعف في الصعود"),
    ]
    choice = random.choice(options)
    signal, reason = choice
    return f"🔎 نتيجة التحليل:\nالعملية: {signal}\nالسبب: {reason}"

# --- استقبال الصور ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = "image.jpg"
    await file.download_to_drive(path)

    result = analyze_image(path)
    await update.message.reply_text(result)

# --- تشغيل البوت ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
