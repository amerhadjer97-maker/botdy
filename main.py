from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =====================
# TOKEN
# =====================
TOKEN = "7996482415:AAFhRRnmu7Fr41zkAa9OHuKntWMeqOwqRaI"

# =====================
# Flask
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅"

# =====================
# Telegram Bot
# =====================
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 البوت يعمل بنجاح ✅")

application.add_handler(CommandHandler("start", start))

# =====================
# Run
# =====================
if __name__ == "__main__":
    application.run_polling()
