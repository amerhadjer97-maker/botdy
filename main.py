# main.py
import os
from io import BytesIO
from PIL import Image, ImageStat
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# قراءة التوكن من متغير البيئة TELEGRAM_TOKEN
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:7996482415:"AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"
    raise RuntimeError("TELEGRAM_TOKEN غير مُعين في متغيرات البيئة")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("أهلاً! أرسل صورة الشارت وسأحلّلها بشكل بسيط (أبعاد ومتوسط سطوع).")

def analyze_image_from_bytes(image_bytes: bytes):
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    stat = ImageStat.Stat(img.convert("L"))
    mean_brightness = stat.mean[0]
    return {
        "width": w,
        "height": h,
        "mean_brightness": mean_brightness
    }

def photo_handler(update: Update, context: CallbackContext):
    msg = update.message
    if not msg.photo:
        update.message.reply_text("لم يتم إرسال صورة صحيحة.")
        return
    # najib أعلى جودة صورة
    photo = msg.photo[-1]
    bio = BytesIO()
    photo.get_file().download(out=bio)
    bio.seek(0)
    info = analyze_image_from_bytes(bio.read())
    reply = (
        f"تحليل بسيط للصورة:\n"
        f"العرض: {info['width']} بكسل\n"
        f"الارتفاع: {info['height']} بكسل\n"
        f"متوسّط السطوع (0-255): {info['mean_brightness']:.1f}\n\n"
        "ملاحظة: هذه نسخة أساسية. لإضافة تحليل الشمعات/اتجاهات نحتاج كود تحليل رسم بياني إضافي."
    )
    update.message.reply_text(reply)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
