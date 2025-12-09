# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥📸 أهلاً! أرسل لي أي صورة وسأحللها لك بدون أي API!")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري تحليل الصورة...")

    photo = update.message.photo[-1]
    file = await photo.get_file()

    img_path = "image.jpg"
    await file.download_to_drive(img_path)

    try:
        # قراءة الصورة
        img = cv2.imread(img_path)

        if img is None:
            await update.message.reply_text("❌ لم أستطع قراءة الصورة!")
            return

        # استخراج نص من الصورة OCR
        text = pytesseract.image_to_string(Image.open(img_path), lang='eng')

        # مثال تحليل بسيط للشارت (اتجاه الشموع)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        white_pixels = np.sum(edges == 255)
        darkness = np.mean(gray)

        trend = "📈 صعود" if darkness < 100 else "📉 هبوط"

        result = f"""
📊 **نتيجة التحليل:**  
الاتجاه العام: {trend}
كمية الخطوط المكتشفة: {white_pixels}
النص الموجود داخل الصورة (OCR):
———————————
{text}
———————————
        """

        await update.message.reply_text(result)

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ أثناء التحليل: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("🚀 البوت يعمل الآن بدون API بنجاح")
    app.run_polling()

if __name__ == "__main__":
    main()
