import telebot
from flask import Flask
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
bot = telebot.TeleBot(BOT_TOKEN)

# ========= BOT HANDLERS =========

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 البوت شغّال بنجاح على Render!\nارسل صورة الشارت الآن 👍")

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.reply_to(message, "📸 تم استلام الصورة! جارٍ التحليل…")
    # يمكنك هنا إضافة كود التحليل أو الردود الخاصة بك


# ========= FLASK SERVER =========

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

# ========= RUN BOT + SERVER =========

if __name__ == "__main__":
    # تشغيل البوت بشكل مستمر
    import threading

    def polling_thread():
        bot.polling(none_stop=True, interval=0, timeout=20)

    thread = threading.Thread(target=polling_thread)
    thread.daemon = True
    thread.start()

    # تشغيل Flask لكي يبقى السيرفر حي على Render
    app.run(host="0.0.0.0", port=10000)
