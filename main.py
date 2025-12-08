import os
import requests
import base64
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==================================================
# 🔐 توكن البوت
# ==================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "7996482415:AAEbB5Eg305FyhddTG_xDrSNdNndVdw2fCI")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ==================================================
# 🔑 مفتاح OpenAI
# ضعه في Render ضمن Environment Variables
# OR ضعه هنا مباشرة (اختياري)
# ==================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ==================================================
# 🟦 إرسال رسالة للمستخدم
# ==================================================
def send_message(chat_id, text):
    try:
        url = BASE_URL + "sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("send_message error:", e)

# ==================================================
# 🟦 تنزيل صورة من تيليجرام
# ==================================================
def download_file(file_path, dest_path):
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()

    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

# ==================================================
# 🧠 تحليل الصورة بواسطة OpenAI Vision
# ==================================================
def analyze_image(image_path):
    try:
        import openai
        openai.api_key = OPENAI_API_KEY

        if not OPENAI_API_KEY:
            return {"error": "⚠️ لم يتم إضافة مفتاح OpenAI في السيرفر."}

        # تحويل الصورة Base64
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode("utf-8")

        prompt = """
        أنت خبير تحليل فني محترف.
        قم بتحليل هذه الصورة (شموع، اتجاه، دعم/مقاومة، حركة لحظية) ثم أعطني:
        - ملخص سريع
        - فرص BUY أو SELL
        - السعر المناسب
        - السبب

        اكتب النتيجة بصيغة JSON فقط:

        {
          "summary": "...",
          "signals": [
            {"type": "BUY أو SELL", "price": "1234.56", "reason": "..."}
          ]
        }
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت خبير تحليل فني محترف."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{encoded}"}
                    ]
                }
            ]
        )

        content = response["choices"][0]["message"]["content"]
        return json.loads(content)

    except Exception as e:
        return {"error": str(e)}

# ==================================================
# 🟩 Webhook — استقبال الرسائل والصور
# ==================================================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if not update:
        return jsonify({"error": "No update"}), 400

    # هل الرسالة موجودة؟
    if "message" not in update:
        return "OK", 200

    msg = update["message"]
    chat_id = msg["chat"]["id"]

    # ========== 📸 لو يوجد صورة ==========
    if "photo" in msg:
        file_id = msg["photo"][-1]["file_id"]

        # الحصول على link الصورة
        file_info = requests.get(BASE_URL + "getFile",
                                 params={"file_id": file_id}).json()

        if not file_info.get("ok"):
            send_message(chat_id, "❌ فشل في جلب ملف الصورة.")
            return "OK", 200

        file_path = file_info["result"]["file_path"]
        local_path = f"/tmp/{os.path.basename(file_path)}"

        try:
            download_file(file_path, local_path)
            analysis = analyze_image(local_path)
        except Exception as e:
            send_message(chat_id, f"❌ خطأ أثناء معالجة الصورة: {e}")
            return "OK", 200

        # طباعة النتيجة
        if "error" in analysis:
            send_message(chat_id, "⚠️ خطأ: " + analysis["error"])
        else:
            text = f"🔍 <b>تحليل الصورة:</b>\n\n"
            text += f"📌 <b>الملخص:</b> {analysis.get('summary','')}\n\n"

            for s in analysis.get("signals", []):
                text += f"➡️ <b>{s['type']}</b> عند السعر <b>{s['price']}</b>\n"
                text += f"📝 السبب: {s['reason']}\n\n"

            send_message(chat_id, text)

        return "OK", 200

    # ========== 📝 نصوص ==========
    text = msg.get("text", "")

    if text == "/start":
        send_message(chat_id, "👋 أهلاً! أرسل صورة الشارت لتحليلها فوراً 🔥")
    else:
        send_message(chat_id, f"📨 استلمت رسالتك:\n{text}")

    return "OK", 200

# ==================================================
# صفحة فحص السيرفر
# ==================================================
@app.route("/", methods=["GET"])
def index():
    return "Bot is running ✔️"

# ==================================================
# تشغيل على Render
# ==================================================
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)
