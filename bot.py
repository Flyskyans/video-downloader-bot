import telebot
import yt_dlp
import os

BOT_TOKEN = "8842366232:AAFhme7NvvP-wZO9YQsJC82YjLB5nurDKec"
CHANNEL_ID = "@ansskyn"
CHANNEL_URL = "https://t.me/ansskyn"

bot = telebot.TeleBot(BOT_TOKEN)

def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print("Ошибка:", e)
        return False

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "👋 Привет! Отправь ссылку на видео из YouTube, Instagram или TikTok.\n\n"
        "Перед скачиванием нужно подписаться на наш канал: " + CHANNEL_URL)

@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.from_user.id
    text = message.text or ""

    if not (text.startswith("http://") or text.startswith("https://")):
        bot.send_message(message.chat.id, "❌ Отправь ссылку на видео.")
        return

    if not check_sub(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 Подписаться", url=CHANNEL_URL))
        markup.add(telebot.types.InlineKeyboardButton("✅ Я подписался", callback_data="check"))
        bot.send_message(message.chat.id,
            "⚠️ Чтобы скачать видео, подпишись на канал:",
            reply_markup=markup)
        return

    download_and_send(message, text)

@bot.callback_query_handler(func=lambda c: c.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Спасибо за подписку!")
        bot.send_message(call.message.chat.id, "Теперь отправь ссылку ещё раз — и я скачаю видео.")
    else:
        bot.answer_callback_query(call.id, "❌ Ты ещё не подписан!", show_alert=True)

def download_and_send(message, url):
    msg = bot.send_message(message.chat.id, "⏳ Скачиваю видео, подожди...")
    try:
        ydl_opts = {
            'outtmpl': '/tmp/%(id)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        bot.edit_message_text("📤 Отправляю видео...", message.chat.id, msg.message_id)

        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ Готово!")

        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {str(e)[:200]}", message.chat.id, msg.message_id)

print("Бот запущен...")
bot.infinity_polling()
