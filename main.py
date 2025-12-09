import os
import requests
import base64
from flask import Flask, request

# ============================
#   BOT TOKEN
# ============================
BOT_TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

app = Flask(__name__)

# ============================
#   إرسال رسالة
# ============================
def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# ============================
#   تحليل الصورة (نسخة مجانية)
# ============================
def analyze_image_free(image_bytes):
    import cv2
    import numpy as np

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return "❌ فشل في قراءة الصورة"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 70, 170)

    # تحليل بسيط لاستخراج مناطق اهتمام
    h, w = edges.shape
    left_intensity = edges[:, :w//3].mean()
    center_intensity = edges[:, w//3:2*w//3].mean()
    right_intensity = edges[:, 2*w//3:].mean()

    strongest = max(left_intensity, center_intensity, right_intensity)

    if strongest == left_intensity:
        zone = "📉 يسار — احتمال هبوط"
    elif strongest == center_intensity:
        zone = "➖ منتصف — ترقب"
    else:
        zone = "📈 يمين — احتمال صعود"

    return f"🔍 نتيجة التحليل:\n{zone}"

# ============================
#   Webhook
# ============================
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]

        # إذا رسالة نصية
        if "text" in message:
            send_message(chat_id, "🤖 البوت شغال! أرسل صورة الشارت لتحليلها.")
        
        # إذا صورة
        if "photo" in message:
            try:
                file_id = message["photo"][-1]["file_id"]
                file_info = requests.get(BASE_URL + f"getFile?file_id={file_id}").json()

                file_path = file_info["result"]["file_path"]
                file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

                img_bytes = requests.get(file_url).content

                result = analyze_image_free(img_bytes)
                send_message(chat_id, result)

            except Exception as e:
                send_message(chat_id, f"❌ خطأ أثناء التحليل: {str(e)}")

    return "OK", 200

# ============================
#   Health Check
# ============================
@app.route("/")
def home():
    return "BOT is running!"

# ============================
#   تشغيل Flask
# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
