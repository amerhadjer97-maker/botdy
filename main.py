
import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update, context):
    await update.message.reply_text("🚀 البوت شغال بنجاح!!")

async def echo(update, context):
    await update.message.reply_text("✔️ تم الاستلام")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling()

if __name__ == "__main__":
    main()
