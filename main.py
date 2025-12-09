import telebot
from flask import Flask, request
import requests
from PIL import Image
import numpy as np
import io

TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# تحليل الصورة عبر HuggingFace مجاناً
def analyze_image(image_bytes):
    url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Authorization": "Bearer hf_xxxxxxxxxxxxxxxxx"}  # اختياري فقط، يمكن تركه فارغاً
    response = requests.post(url, headers=headers, data=image_bytes)

    try:
        return response.json()[0]["generated_text"]
    except:
        return "❌ لم أستطع تحليل الصورة."

@bot.message_handler(content_types=["photo"])
def handle_image(message):
    file_id = message.photo[-1].file_id
    file = bot.get_file(file_id)
    image_data = bot.download_file(file.file_path)
    
    result = analyze_image(image_data)
    bot.reply_to(message, "🔍 تحليل الصورة:\n\n" + result)

@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
