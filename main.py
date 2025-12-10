from pyrogram import Client, filters

# ---------------- إعدادات البوت ----------------
API_ID = 123456   # ضع API_ID الخاص بك
API_HASH = "api_hash_here"   # ضع API_HASH الخاص بك
BOT_TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"

app = Client(
    "tradbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- دالة تحليل الصورة ----------------
def analyze_image(image_path):
    # لاحقاً نضع تحليل حقيقي
    return {
        "sell_price": "1495.20",
        "sell_reason": "مؤشر RSI عالي + شمعة انعكاس",
        "buy_price": "1492.50",
        "buy_reason": "دعم قوي عند هذا المستوى"
    }

# ---------------- استقبال الصور ----------------
@app.on_message(filters.photo)
def handle_photo(client, message):

    file_path = client.download_media(message.photo.file_id)

    analysis = analyze_image(file_path)

    reply_text = f"""
🔎 **تحليل الصورة:**
مثال تحليل تلقائي. استبدل `analyze_image` باستدعاء نموذج حقيقي.

**- SELL | السعر: {analysis['sell_price']}**
السبب: {analysis['sell_reason']}

**- BUY | السعر: {analysis['buy_price']}**
السبب: {analysis['buy_reason']}
"""

    message.reply_text(reply_text)

# ---------------- تشغيل البوت ----------------
app.run()
