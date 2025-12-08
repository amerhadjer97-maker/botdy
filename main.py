import requests
import time

# ============================
#      BOT TOKEN
# ============================
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

LAST_UPDATE_ID = 0

# ============================
#      ارسال رسالة
# ============================
def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# ============================
#      قراءة الرسائل
# ============================
def get_updates():
    url = BASE_URL + "getUpdates"
    params = {
        "offset": LAST_UPDATE_ID + 1
    }
    response = requests.get(url, params=params)
    return response.json()

# ============================
#      معالجة الرسائل
# ============================
def handle_message(message):
    chat_id = message["message"]["chat"]["id"]
    text = message["message"].get("text", "")

    if text == "/start":
        send_message(chat_id, "مرحبا! البوت يعمل الآن بنجاح 😄🔥")

    else:
        send_message(chat_id, f"لقد استقبلت رسالتك: {text}")

# ============================
#      حلقة التشغيل
# ============================
def main():
    global LAST_UPDATE_ID

    while True:
        updates = get_updates()

        if "result" in updates:
            for update in updates["result"]:
                LAST_UPDATE_ID = update["update_id"]
                handle_message(update)

        time.sleep(1)

# ============================
#      تشغيل البوت
# ============================
if __name__ == "__main__":
    main()
