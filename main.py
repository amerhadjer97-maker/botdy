import os
import requests
import time

# ============================
#   BOT TOKEN
# ============================
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

LAST_UPDATE_ID = 0

def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    send_message(chat_id, f"مرحبا! استلمت رسالتك: {text}")

def get_updates(offset=None):
    url = BASE_URL + "getUpdates"
    params = {"timeout": 30, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

def main():
    global LAST_UPDATE_ID
    print("🤖 Bot is running with POLLING...")

    while True:
        updates = get_updates(LAST_UPDATE_ID + 1)

        if "result" in updates:
            for update in updates["result"]:
                LAST_UPDATE_ID = update["update_id"]

                if "message" in update:
                    handle_message(update["message"])

        time.sleep(1)

if __name__ == "__main__":
    main()
