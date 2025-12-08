import os
from flask import Flask, request
import requests

app = Flask(__name__)

# ==============================
#   Telegram BOT TOKEN
# ==============================
BOT_TOKEN = os.getenv("7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI")  # اجلب التوكن من Environment Variables
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"


# ==============================
#   Webhook route
# ==============================
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # رد بسيط للتجربة
        send_message(chat_id, f"تم استلام رسالتك: {text}")

    return "OK", 200


# ==============================
#   إرسال رسالة
# ==============================
def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


# ==============================
#   Main
# ==============================
@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
