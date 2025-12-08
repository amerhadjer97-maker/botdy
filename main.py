import os
from flask import Flask, request
import requests

app = Flask(__name__)

# ============================
# BOT TOKEN
# ============================
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"


# ============================
# إرسال رسالة
# ============================
def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


# ============================
# Webhook
# ============================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "البوت يعمل بنجاح على Render! 🔥")
        else:
            send_message(chat_id, f"استلمت رسالتك: {text}")

    return "OK", 200


# ============================
# الصفحة الرئيسية
# ============================
@app.route("/")
def home():
    return "Bot is running!", 200


# ============================
# Main
# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
