import os
from flask import Flask, request
from telegram import Bot

# ======================
# TOKEN (7996482415:AAFhRRnmu7Fr41zkAa9OHuKntWMeqOwqRaI)
# ======================
TOKEN = "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE"

bot = Bot(token=TOKEN)

# ======================
# Flask App
# ======================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # مثال رسالة من TradingView
    message = f"""
📊 TradingView Alert
--------------------
Symbol: {data.get('symbol')}
Signal: {data.get('signal')}
Price: {data.get('price')}
Time: {data.get('time')}
"""

    # ضع ID حسابك في تيليغرام
    CHAT_ID = "PUT_YOUR_CHAT_ID_HERE"

    bot.send_message(chat_id=CHAT_ID, text=message)
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
