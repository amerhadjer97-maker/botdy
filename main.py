import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==================================================
# ضع توكن البوت هنا (حسب طلبك — هذا التوكن الذي أعطيتني إياه)
# ==================================================
BOT_TOKEN = "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ==================================================
# (اختياري) مفتاح OpenAI - اتركه فارغاً إذا لم يكن لديك
# لو عندك مفتاح ضع قيمته هنا قبل استخدام analyze_with_openai
# ==================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # أو ضع المفتاح هنا كسلسلة

# ==================================================
# تنزيل ملف من Telegram (file_path => file_url => تنزيل)
# ==================================================
def download_file(file_path, dest_path):
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    r = requests.get(file_url, stream=True, timeout=30)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

# ==================================================
# إرسال رسالة إلى الدردشة
# ==================================================
def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("send_message error:", e)

# ==================================================
# محلّل الصورة (مثال) - هنا تضيف منطقك أو تستدعي OpenAI/نموذج
# ترجع dict بسيط يحوي اماكن الدخول والسبب والسعر المقترح
# ==================================================
def analyze_image(image_path):
    # >>> هنا ضع التحليل الحقيقي: نموذج ML أو استدعاء API
    # إذا لم تستخدم أي API الآن، أرجع نتيجة تجريبية (مثال)
    result = {
        "signals": [
            {"type": "SELL", "reason": "مؤشر RSI عالي + شمعة انعكاس", "price": "1495.20"},
            {"type": "BUY",  "reason": "دعم قوي عند هذا المستوى",        "price": "1492.50"}
        ],
        "summary": "مثال تحليل تلقائي. استبدل analyze_image باستدعاء نموذج حقيقي."
    }
    return result

# مثال توضيحي لو أردت استدعاء OpenAI (pseudo)
def analyze_with_openai(image_path):
    if not OPENAI_API_KEY:
        raise RuntimeError("OpenAI API key not configured.")
    # هنا تضع كود الاستدعاء لواجهة OpenAI Vision أو model آخر
    # (هذا جزء توضيحي فقط — تحتاج تثبيت المكتبة واستخدام endpoint الصحيح)
    return analyze_image(image_path)  # مؤقتاً

# ==================================================
# معالجة رسالة واردة من Telegram (webhook)
# ==================================================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"status": "no data"}), 400

    # رسالة نصية عادية
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]

        # لو هناك صورة (photos)
        if "photo" in msg:
            # Telegram يرسل عدة أحجام للـ photo => آخِر عنصر هو الأكبر عادة
            photo_sizes = msg["photo"]
            file_id = photo_sizes[-1]["file_id"]

            # نجيب معلومات الملف
            r = requests.get(BASE_URL + "getFile", params={"file_id": file_id}, timeout=10).json()
            if r.get("ok"):
                file_path = r["result"]["file_path"]
                local_path = f"/tmp/{os.path.basename(file_path)}"
                try:
                    download_file(file_path, local_path)
                    # تحليل الصورة
                    try:
                        analysis = analyze_image(local_path)
                    except Exception as e:
                        analysis = {"error": str(e)}
                    # إرسال نتيجة مبسطة للمستخدم
                    if "signals" in analysis:
                        texts = [f"🔎 تحليل الصورة:\n" + analysis.get("summary", "")]
                        for s in analysis["signals"]:
                            texts.append(f"- {s['type']} | السعر: {s['price']}\n  السبب: {s['reason']}")
                        send_message(chat_id, "\n\n".join(texts))
                    else:
                        send_message(chat_id, "تعذر تحليل الصورة: " + str(analysis.get("error", "خطأ غير معروف")))
                except Exception as e:
                    send_message(chat_id, "خطأ أثناء تنزيل الصورة: " + str(e))
            else:
                send_message(chat_id, "فشل في جلب ملف الصورة من Telegram.")
            return "OK", 200

        # أو رسالة نصية
        text = msg.get("text", "")
        # أوامر بسيطة
        if text == "/start":
            send_message(chat_id, "مرحباً! أرسل صورة لتحليلها.")
        else:
            send_message(chat_id, f"استلمت رسالتك: {text}")

    return "OK", 200

# ==================================================
# Route للمراجعة
# ==================================================
@app.route("/", methods=["GET"])
def index():
    return "Bot is running (webhook mode)."

# ==================================================
# تشغيل السيرفر: رتب على أن يستخدم المتغير PORT من البيئة (مهم على Render)
# ==================================================
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)
