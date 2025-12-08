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
