# -*- coding: utf-8 -*-
import os
import base64
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋🔥 أهلاً! أرسل لي أي صورة وسأحللها لك باحترافية!")


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري تحليل الصورة...")

    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_path = "image.jpg"
    await file.download_to_drive(img_path)

    try:
        # تحويل الصورة إلى Base64
        with open(img_path, "rb") as img:
            img_base64 = base64.b64encode(img.read()).decode("utf-8")

        # طلب API مجاني
        response = requests.post(
            "https://api.gemini.amerhadjer.me/analyze",
            json={"image": img_base64}
        )

        if response.status_code != 200:
            await update.message.reply_text("❌ خطأ من السيرفر المجاني!")
            return

        result = response.json().get("result", "❌ لم أستطع فهم الصورة.")

        await update.message.reply_text(
            f"📊 **النتيجة:**\n\n{result}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء تحليل الصورة:\n{str(e)}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("🚀 البوت يعمل الآن بدون مشاكل UTF-8…")
    app.run_polling()


if __name__ == "__main__":
    main()
