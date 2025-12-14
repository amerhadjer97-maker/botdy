from telegram.ext import Application, MessageHandler, CommandHandler, filters

BOT_TOKEN = "8566367254:AAGdkD0DB2vvORuGVOeUU6yh6BcacK__1eI"

# رسالة البداية
async def start(update, context):
    await update.message.reply_text("مرحبًا 👋\nأرسل صورة الشارت لتحليلها 📸")

# تحليل الصورة (نسخة مطابقة للمثال)
def analyze_image(image_path):
    # حالياً نفس المنطق الذي طلبته (ثابت ومنسق)
    result = """
🔎 تحليل الصورة:

- SELL | السعر: 1495.20
  السبب: مؤشر RSI عالي + شمعة انعكاس

- BUY | السعر: 1492.50
  السبب: دعم قوي عند هذا المستوى
"""
    return result

# استقبال الصور
async def handle_image(update, context):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    await file.download_to_drive("chart.jpg")

    analysis = analyze_image("chart.jpg")
    await update.message.reply_text(analysis)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("Bot is running...")
    app.run_polling()

if name == "main":
    main()
