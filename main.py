import telebot
from flask import Flask, request
import os
import requests
import base64

BOT_TOKEN = os.getenv("7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ========= تحليل الصورة =========

def analyze_image(image_path):
    with open(image_path, "rb") as img:
        img_b64 = base64.b64encode(img.read()).decode("utf-8")

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    prompt = """
أنت خبير تحليل فني محترف...
(نفس النص الذي وضعته أنت)
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    return result["choices"][0]["message"]["content"]

# ========= TELEGRAM BOT =========

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 البوت يعمل بنجاح!\nأرسل صورة الشارت الآن وسيتم التحليل.")

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.reply_to(message, "📸 تم استلام الصورة! جارٍ التحليل…")

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    image_path = "chart.png"
    with open(image_path, "wb") as new_file:
        new_file.write(downloaded)

    analysis = analyze_image(image_path)
    bot.send_message(message.chat.id, analysis)

# ========= WEBHOOK SERVER =========

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_data = request.stream.read()
    update = telebot.types.Update.de_json(json_data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def home():
    return "Bot is running!", 200

# ========= START FLASK =========

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
