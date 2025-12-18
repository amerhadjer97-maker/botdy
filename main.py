from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "7996482415:AAFhRRnmu7Fr41zkAa9OHuKntWMeqOwqRaI"

app = Flask(__name__)

# Telegram application
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 البوت يعمل عبر Webhook ✅")

application.add_handler(CommandHandler("start", start))

# Telegram webhook
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

# Home
@app.route("/")
def home():
    return "Webhook Bot is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
