import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

def start(update, context):
    update.message.reply_text("البوت شغال بنجاح 🎉🔥")

def echo(update, context):
    update.message.reply_text("تم الاستلام ✔️")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
