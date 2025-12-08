import requests
import time

BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

LAST_UPDATE_ID = 0

def get_updates(offset=None):
    url = BASE_URL + "getUpdates"
    params = {"timeout": 60, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    params = {"chat_id": chat_id, "text": text}
    requests.get(url, params=params)

def main():
    global LAST_UPDATE_ID

    while True:
        try:
            updates = get_updates(LAST_UPDATE_ID + 1)
            if "result" in updates:
                for update in updates["result"]:
                    LAST_UPDATE_ID = update["update_id"]
                    chat_id = update["message"]["chat"]["id"]
                    msg_text = update["message"].get("text", "")

                    send_message(chat_id, f"Received: {msg_text}")

        except Exception as e:
            print("ERROR:", e)

        time.sleep(1)

if __name__ == "__main__":
    main()
