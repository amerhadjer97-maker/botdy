import telebot
from flask import Flask, request
import cv2
import numpy as np
import pytesseract
from PIL import Image

# ============================
#     TELEGRAM CONFIG
# ============================
TOKEN = "7996482415:AAHEPHHVflgsuDJkG-LUyfB2WCJRtnWZbZE"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ============================
#   IMAGE ANALYSIS FUNCTION
# ============================

def analyze_image(image_path):
    try:
        img = cv2.imread(image_path)

        if img is None:
            return "⚠️ لم أتمكن من قراءة الصورة!"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_string(gray, lang="eng")

        analysis = ""

        edges = cv2.Canny(gray, 50, 150)
        edge_sum = np.sum(edges)

        if edge_sum > 1500000:
            trend = "📉 الترند هابط بقوة"
        elif edge_sum > 900000:
            trend = "📈 الترند صاعد"
        else:
            trend = "⚠️ السوق جانبي"

        analysis += trend + "\n\n"

        brightness = np.mean(gray)

        if brightness > 160:
            analysis += "🔆 الشموع فاتحة… ربما صعود قوي\n"
        elif brightness < 80:
            analysis += "🌑 الشموع داكنة… ضغط بيعي\n"
        else:
            analysis += "🌓 السوق متوازن\n"

        density = int(edge_sum / 100000)
        analysis += f"📊 قوة الحركة: {density}/20\n"

        result = (
            "🔍 **تحليل الصورة:**\n\n"
            f"{analysis}\n"
            "📄 **النص المستخرج من الصورة:**\n"
            f"```\n{text}\n```"
        )

        return result

    except Exception as e:
        return f"❌ خطأ أثناء تحليل الصورة: {str(e)}"


# ============================
#     TELEGRAM HANDLERS
# ============================

@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.reply_to(message,
        "🔥 أهلاً بك! أرسل لي أي صورة وسأعطيك تحليل احترافي مباشرة!\n"
        "يدعم: شارت – صفقات – شموع – أرقام – كتابة."
    )

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        img_path = "input_img.jpg"
        with open(img_path, "wb") as f:
            f.write(downloaded)

        bot.reply_to(message, "⏳ جاري تحليل الصورة…")

        result = analyze_image(img_path)

        bot.reply_to(message, result)

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")


# ============================
#        FLASK SERVER
# ============================

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = request.get_data().decode("utf-8")
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "🔥 Bot is running without OpenAI!"

# ============================

if __name__ == "__main__":
    bot.infinity_polling()
