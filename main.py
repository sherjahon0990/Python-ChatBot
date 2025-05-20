import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import logging
import requests

TOKEN = '7872116107:AAHuY3GZYvar47QZzvfj6vaiErIwnQwjv-I'
bot = telebot.TeleBot(TOKEN)
url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"

response = requests.get(url)
# chat_id mapping
chat_to_user = {}
user_to_chat = {}

logging.basicConfig(level=logging.INFO)

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Chatni boshlash"))
    bot.send_message(chat_id, "Salom! Quyidagi tugmani bosing:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Chatni boshlash")
def ask_chat_id(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Foydalanuvchining ID raqamini kiriting:", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, register_chat)

def register_chat(message):
    chat_id = message.chat.id
    user = message.text.strip()

    try:
        user_id = int(user)
    except ValueError:
        bot.send_message(chat_id, "❗ Iltimos, foydalanuvchining ID raqamini kiriting (faqat raqam bo‘lishi kerak).")
        bot.register_next_step_handler(message, register_chat)
        return

    # Avval, bu foydalanuvchiga bot yozoladimi, tekshiramiz
    try:
        bot.send_message(user_id, "👋 Sizga xabar yuborilmoqda. Agar bu siz kutgan bo‘lsa, bu botdan chiqmang.")
    except Exception as e:
        logging.error(f"Foydalanuvchi {user_id} ga xabar yuborishda xato: {e}")
        bot.send_message(chat_id, "❗ Bu foydalanuvchi hali botga /start yubormagan. Iltimos, undan botni ochib /start buyrug‘ini yuborishini so‘rang.")
        return

    chat_to_user[chat_id] = user_id
    user_to_chat[user_id] = chat_id

    bot.send_message(chat_id, "✅ Endi matn yozishingiz mumkin.")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text

    # Javob yuborayotgan foydalanuvchidan xabar
    if chat_id in user_to_chat:
        original_chat_id = user_to_chat[chat_id]
        try:
            bot.send_message(original_chat_id, text)
        except Exception as e:
            logging.error(f"Xabarni {original_chat_id} ga yuborishda xato: {e}")
        return

    # Xabar kimga yuborilishi kerakligini tekshiramiz
    user = chat_to_user.get(chat_id)
    if not user:
        bot.send_message(chat_id, "❗ Iltimos, avval 'Chatni boshlash' tugmasi orqali foydalanuvchi ID raqamini kiriting.")
        return

    try:
        bot.send_message(user, text)
    except Exception as e:
        logging.error(f"Xabarni {user} ga yuborishda xato: {e}")



if response.ok:
    print("✅ Webhook muvaffaqiyatli o‘chirildi.")
else:
    print("❌ Xatolik:", response.text)
print('Bot ishga tushdi')
bot.polling()
