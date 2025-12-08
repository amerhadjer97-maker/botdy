import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from PIL import Image

# BOT TOKEN
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"

# تحليل مجاني للصورة (بدون OpenAI)
def analyze_image_local(image_path):
    try:
        img = Image.open(image_path)
        pixels = img.convert("L").load()  # تحويل للصورة الرمادية

        width, height = img.size
        center_pixel = pixels[width // 2, height // 2]

        if center_pixel < 90:
            return "📉 السوق يبدو هابطاً بناءً على كثافة الألوان الداكنة."
        elif center_pixel > 170:
            return "📈 السوق يبدو صاعداً مع ألوان فاتحة."
        else:
            return "〰️ السوق في حالة تذبذب، لا يوجد اتجاه واضح."
    except:
        return "⚠️ لم أستطع تحليل الصورة. حاول إرسال لقطة شاشة أوضح."

# استقبال الصور
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_path = "received_image.jpg"
    await file.download_to_drive(image_path)

    result = analyze_image_local(image_path)
    await update.message.reply_text(result)

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🚀 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
