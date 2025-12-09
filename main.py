import logging
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from PIL import Image
import io

# ======================================================
# 🚀 ضع التوكن تاعك هنا فقط !!
BOT_TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"
# ======================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update, context):
    await update.message.reply_text("🔥 البوت شغال! أرسل صورة باش نحللها.")

async def analyze_image(update, context):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()

    # مثال تحليل بسيط
    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size

    await update.message.reply_text(
        f"📸 تم استلام صورة!\n\nالعرض: {width}px\nالارتفاع: {height}px\n\nجاهز نزيد تحليل احترافي!"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))

    app.run_polling()

if __name__ == "__main__":
    main()
