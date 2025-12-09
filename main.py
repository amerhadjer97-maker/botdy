import os
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"

REPLICATE_API_TOKEN = "ضع_توكن_ريبيكيت_هنا"

def analyze_image(img_bytes):
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    files = {"file": ("image.jpg", img_bytes, "image/jpeg")}
    upload_res = requests.post("https://api.replicate.com/v1/files",
                               headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"},
                               files=files).json()

    image_url = upload_res["urls"]["get"]

    payload = {
        "version": "llava-13b",
        "input": {
            "image": image_url,
            "prompt": "Provide a detailed analysis of this trading chart."
        }
    }

    res = requests.post(url, json=payload, headers=headers).json()
    prediction_url = res["urls"]["get"]

    while True:
        final = requests.get(prediction_url, headers=headers).json()
        if final["status"] == "succeeded":
            return final["output"]
        elif final["status"] == "failed":
            return "❌ حدث خطأ أثناء التحليل"
            

def handle_image(update: Update, context: CallbackContext):
    file = update.message.photo[-1].get_file()
    img_bytes = file.download_as_bytearray()

    update.message.reply_text("⏳ جاري تحليل الصورة...")

    result = analyze_image(img_bytes)
    update.message.reply_text(f"📊 نتيجة التحليل:\n\n{result}")


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
