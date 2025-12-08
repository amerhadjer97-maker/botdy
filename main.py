import os
import cv2
import pytesseract
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image
import tempfile

#==============================
#     BOT TOKEN
#==============================
BOT_TOKEN = " 7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI "

#==============================
#   تحليل الشارت من الصورة
#==============================
def analyze_chart(image_path):
    # قراءة الصورة
    img = cv2.imread(image_path)

    if img is None:
        return "❌ لا يمكن قراءة الصورة"

    # تحويل إلى رمادي
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # استخراج النص (الأرقام – الأسعار)
    text = pytesseract.image_to_string(gray)

    # تحليل بسيط جداً للشارت
    img_mean = np.mean(gray)

    trend = ""
    if img_mean > 130:
        trend = "📈 الترند غالباً صاعد"
    else:
        trend = "📉 الترند غالباً هابط"

    # استخراج أسعار تقريبية لو موجودة
    numbers = []
    for part in text.split():
        try:
            number = float(part.replace(",", "."))
            numbers.append(number)
        except:
            pass

    if numbers:
        max_price = max(numbers)
        min_price = min(numbers)
    else:
        max_price = None
        min_price = None

    # بناء الرد
    result = f"""🔥 **نتيجة تحليل الصورة:**

{text}

{trend}

"""

    if max_price and min_price:
        result += f"🔹 أعلى رقم بالتحليل: {max_price}\n"
        result += f"🔹 أدنى رقم بالتحليل: {min_price}\n"

    result += "\n⚡ التحليل مجاني بدون أي API"

    return result


#==============================
#   START COMMAND
#==============================
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "مرحباً! 👋\n"
        "أرسل صورة الشارت الآن لتحليلها فوراً 🔥"
    )

#==============================
#   استقبال الصور
#==============================
def handle_image(update: Update, context: CallbackContext):
    try:
        file = update.message.photo[-1].get_file()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            file.download(custom_path=tmp.name)
            result = analyze_chart(tmp.name)

        update.message.reply_text(result)

    except Exception as e:
        update.message.reply_text(f"❌ حدث خطأ: {e}")

#==============================
#      MAIN
#==============================
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
