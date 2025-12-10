import telebot  
from PIL import Image  
import numpy as np  
  
# مفتاح البوت  
TOKEN = "7996482415:AAHS2MmIVnx5-Z4w5ORcntmTXDg16u8JTqs"  
bot = telebot.TeleBot(TOKEN)  
  
# دالة تحليل الصورة (مؤقتة)  
def analyze_image(image_path):  
    # استبدل هذا الجزء بخوارزميات حقيقية لتحليل الرسوم البيانية  
    # هنا مثال بسيط فقط  
    result = {  
        "action": "SELL",  
        "price": 1495.20,  
        "reason": "مؤشر RSI عالي + شمعة انعكاس"  
    }  
    return result  
  
# التعامل مع الصور المرسلة  
@bot.message_handler(content_types=['photo'])  
def handle_photo(message):  
    try:  
        # الحصول على الصورة من تلغرام  
        file_info = bot.get_file(message.photo[-1].file_id)  
        downloaded_file = bot.download_file(file_info.file_path)  
  
        # حفظ الصورة محليًا  
        path = "chart.jpg"  
        with open(path, "wb") as f:  
            f.write(downloaded_file)  
  
        # تحليل الصورة  
        result = analyze_image(path)  
  
        # إرسال النتيجة للمستخدم  
        response = f"🔎 تحليل الصورة:\n" \  
                   f"- {result['action']} | السعر: {result['price']}\n" \  
                   f"السبب: {result['reason']}"  
        bot.reply_to(message, response)  
    except Exception as e:  
        bot.reply_to(message, f"⚠️ حدث خطأ أثناء تحليل الصورة: {e}")  
هل خاذ الكود اضعه في mainpy
