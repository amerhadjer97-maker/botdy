import cv2
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


# ضع التوكن الخاص بك هنا
TELEGRAM_TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"
7996482415:

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 أهلاً! أرسل لي أي صورة شارت وسأعطيك تحليل جاهز + مناطق الدخول."
    )


# ---------------------------------------------------------
# 🔥 تحليل جاهز بالشكل الذي تريده
# ---------------------------------------------------------
def generate_fake_analysis():
    analysis = (
        "🔎 **تحليل الصورة:**\n"
        "مثال تحليل تلقائي. (تحليل تجريبي الآن)\n\n"
        "- **SELL** | السعر: 1495.20  \n"
        "  **السبب:** مؤشر RSI عالي + شمعة انعكاس\n\n"
        "- **BUY** | السعر: 1492.50  \n"
        "  **السبب:** دعم قوي عند هذا المستوى\n"
    )
    return analysis


def handle_image(update: Update, context: CallbackContext):
    file = update.message.photo[-1].get_file()
    file.download("received.png")

    update.message.reply_text("⏳ جارٍ تحليل الصورة...")

    # استدعاء التحليل الجديد
    analysis = generate_fake_analysis()
    update.message.reply_text(analysis)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
