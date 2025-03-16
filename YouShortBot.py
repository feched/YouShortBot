import os
from yt_dlp import YoutubeDL
import telebot

# Инициализация бота
bot = telebot.TeleBot('ВАШ ТОКЕН')

# канал, подпишитесь;)
CHANNEL_ID = '@workshop_on_Grisha'

# Функция для проверки подписки
def is_subscribed(user_id):
    try:
        # Получаем информацию о пользователе в канале
        chat_member = bot.get_chat_member(CHANNEL_ID, user_id)
        # Проверяем, является ли пользователь участником канала
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, 'Привет! Я бот, который скачивает YouTube Shorts и отправляет их тебе. Просто отправь мне ссылку на Shorts.')
    else:
        bot.send_message(message.chat.id, f'Подпишись на канал {CHANNEL_ID}, чтобы использовать этого бота.')

# Обработчик текстовых сообщений (ссылок)
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Проверяем подписку
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, f'Подпишись на канал {CHANNEL_ID}, чтобы использовать этого бота.')
        return

    # Проверяем, что сообщение содержит ссылку на YouTube Shorts
    if 'youtube.com/shorts/' in message.text or 'youtu.be/' in message.text:
        bot.send_message(message.chat.id, 'Скачиваю видео...')

        # Скачиваем видео
        video_path = download_youtube_short(message.text)

        if video_path:
            # Отправляем видео пользователю
            with open(video_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)
            bot.send_message(message.chat.id, 'Видео успешно отправлено!')

            # Удаляем временный файл
            os.remove(video_path)
        else:
            bot.send_message(message.chat.id, 'Не удалось скачать видео. Проверь ссылку и попробуй снова.')
    else:
        bot.send_message(message.chat.id, 'Это не похоже на ссылку на YouTube Shorts. Попробуй снова.')

# Функция для скачивания YouTube Shorts
def download_youtube_short(video_url, output_path='downloads'):
    # Создаем папку для загрузок, если её нет
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Настройки для yt-dlp
    ydl_opts = {
        'format': 'best',  # Скачиваем лучшее качество
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Путь для сохранения
        'quiet': True,  # Отключаем лишние выводы в консоль
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_filename = ydl.prepare_filename(info_dict)
            return video_filename
    except Exception as e:
        print(f"Ошибка при скачивании видео: {e}")
        return None

# Запуск бота
if __name__ == "__main__":
    bot.infinity_polling()