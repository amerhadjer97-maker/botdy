import os
import replicate
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# -----------------------------
# 🔥 هنا وضعنا التوكن الخاص بك
# -----------------------------
BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"

# ضع هنا توكن ريبيكيت الخاص بك
REPLICATE_API_TOKEN = "ضع_توكن_Replicate_هنا"

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN


async def analyze_image(image_path):
    try:
        output = replicate.run(
            "yorickvp/llava-13b",
            input={"image": open(image_path, "rb"), "prompt": "Describe this image in detail."}
        )
        return output
    except Exception as e:
        return f"❌ خطأ أثناء تحليل الصورة: {str(e)}"


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat_id

    await message.reply_text("⏳ جاري تحليل الصورة...")

    file = await message.photo[-1].get_file()
    image_path = "received_image.jpg"
    await file.download_to_drive(image_path)

    result = await analyze_image(image_path)
    await message.reply_text(f"📊 **النتيجة:**\n{result}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً! أرسل لي أي صورة وسأحللها لك 🔍🔥")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("🚀 البوت يعمل الآن!")
    app.run_polling()


if __name__ == "__main__":
    main()
