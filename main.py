import telebot
from flask import Flask, request
import requests

TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# تحليل الصورة عبر API مجاني (HuggingFace مجاناً)
def analyze_image(image_bytes):
    url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Content-Type": "application/octet-stream"}

    response = requests.post(url, headers=headers, data=image_bytes)

    try:
        data = response.json()
        return data[0]["generated_text"]
    except:
        return "❌ لم أستطع تحليل الصورة."

@bot.message_handler(content_types=["photo"])
def handle_image(message):
    file_id = message.photo[-1].file_id
    
    file_info = bot.get_file(file_id)
    image_data = bot.download_file(file_info.file_path)

    result = analyze_image(image_data)
    bot.reply_to(message, f"🔍 **تحليل الصورة:**\n\n{result}")

# Webhook
@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    json_data = request.stream.read().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
