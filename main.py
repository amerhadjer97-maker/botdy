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
def analyze_image(image_path):
    import base64, requests, os

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # قراءة الصورة Base64
    with open(image_path, "rb") as img:
        img_b64 = base64.b64encode(img.read()).decode("utf-8")

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    prompt = """
أنت خبير تحليل فني محترف.  
حلل هذا الشارت كأنك محلل محترف يتعامل مع متداول مبتدئ.

❗أعطني التحليل بالصيغة التالية فقط:

========================
📈 **الاتجاه العام للسوق:**  
- هل هو صاعد / هابط / عرضي؟ ولماذا؟  
- ما الدليل من الشموع والترند؟

📌 **نقطة الدخول المقترحة:**  
- أعطني سعر منطقي واضح أدخل منه  
- ولماذا هذه النقطة بالضبط؟

🛑 **متى يمنع الدخول؟**  
- أعطني 2–3 أسباب واضحة تجعل الصفقة خطيرة.  
- (مثال: شمعة انعكاسية – ضعف حجم الحركة – تشبع RSI)

🎯 **أهداف الربح:**  
- الهدف 1  
- الهدف 2  

🛡 **وقف الخسارة المقترح:**  
- مكانه ولماذا؟

📊 **تحليل المؤشرات (RSI):**  
- هل هو فوق 70 (تشبع شراء)؟  
- أم تحت 30 (تشبع بيع)؟  
- ماذا يعني بالنسبة للصفقة؟

🕯 **تحليل الشموع:**  
- هل توجد شموع انعكاسية؟  
- ابتلاع شرائي / بيعي؟  
- ظل طويل يدل على رفض السعر؟

📌 **الدعم والمقاومة:**  
- أقرب دعم  
- أقرب مقاومة  
- ما المتوقع إذا كسرها؟

💡 **الخلاصة النهائية:**  
- هل الصفقة مناسبة أم لا؟  
- وما أفضل قرار الآن؟
========================

اكتب الإجابات بشكل مفصل وواضح وبنقاط.  
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
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    return result["choices"][0]["message"]["content"]
