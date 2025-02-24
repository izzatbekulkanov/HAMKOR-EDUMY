import requests

# ✅ Telegram bot ma'lumotlari
TOKEN = "7699885631:AAGT34PFryofNop_5IT5PesYcgJpE7X1m7U"
CHAT_ID = "@english_house_lms"  # Kanal username yoki -100XXXXXXXXXX shaklidagi ID
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"




def send_telegram_message(message, success=True):
    """Xabarni Telegram kanalga yuborish."""



    bot_token = "7699885631:AAGT34PFryofNop_5IT5PesYcgJpE7X1m7U"
    chat_id = "@english_house_lms"  # Kanal username yoki -100XXXXXXXXXX shaklidagi ID
    sticker = "✅" if success else "❌"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"{sticker} {message}",
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"❌ Telegramga xabar yuborishda xatolik: {response.text}")
            return False
        return True
    except Exception as e:
        print(f"❌ Telegram so'rovini yuborishda xatolik: {e}")
        return False
