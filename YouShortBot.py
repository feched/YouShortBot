import os
from yt_dlp import YoutubeDL
import telebot

# Инициализация бота
bot = telebot.TeleBot('ВАШ ТОКЕН')

# ID канала (например, @username или ID канала)
CHANNEL_ID = '@workshop_on_Grisha'  # Замени на username или ID своего канала


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
        bot.send_message(message.chat.id,
                         'Привет! Я бот, который скачивает YouTube Shorts и TikTok и отправляет их тебе. Просто отправь мне ссылку на Shorts.\n\nТак же у меня есть команды /start, /help и /partners')
    else:
        bot.send_message(message.chat.id, f'Подпишись на канал {CHANNEL_ID}, чтобы использовать этого бота.')


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_welcome(message):
    if is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id,
                         'Давай я тебе помогу, мой милый друг!\n\nЯ бот который делает одну и очень простую функцию - скачиваю видео из YouTube Short и TikTok.\n\nЕсли я тебе выдал ошибку и ты уверен(а) в том, что виновата серверная часть, напиши вот сюда @Im_tooo, полностью опиши проблему и скинь все скриншоты или перешли сообщения.\n\nАдминистрация обязательно поможет!')
    else:
        bot.send_message(message.chat.id, f'Подпишись на канал {CHANNEL_ID}, чтобы использовать этого бота.')

# Обработчик команды /partners
@bot.message_handler(commands=['partners'])
def send_welcome(message):
    if is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id,
                         'Наши партнёры:\n\nТелеграм канал создателя - https://t.me/workshop_on_Grisha\n\nБонгоКетГолосование - https://t.me/bongocatchannel')
    else:
        bot.send_message(message.chat.id, f'Подпишись на канал {CHANNEL_ID}, чтобы использовать этого бота.')

# Обработчик сылок
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, f'Подпишись на канал {CHANNEL_ID}, чтобы использовать этого бота.')
        return

    try:
        if 'youtube.com/shorts/' in message.text or 'youtu.be/' in message.text or 'tiktok.com/' in message.text:
            bot.send_message(message.chat.id, 'Скачиваю видео...')

            # Определяем, какая платформа
            if 'tiktok.com/' in message.text:
                video_path, video_info = download_tiktok_video(message.text)
            else:
                video_path, video_info = download_youtube_short(message.text)

            if video_path:
                with open(video_path, 'rb') as video_file:
                    bot.send_video(message.chat.id, video_file)

                # Отправляем описание видео
                description = format_video_info(video_info)
                bot.send_message(message.chat.id, description, parse_mode='HTML')

                os.remove(video_path)
            else:
                bot.send_message(message.chat.id, 'Не удалось скачать видео. Попробуйте другую ссылку.')
        else:
            bot.send_message(message.chat.id, 'Это не похоже на ссылку YouTube Shorts или TikTok.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {str(e)}')


def format_video_info(info_dict):
    """Форматирует информацию о видео в читаемый текст"""
    description = "<b>Информация о видео:</b>\n\n"

    if 'title' in info_dict:
        description += f"<b>Описание:</b> {info_dict['title']}\n"

    return description


# Функция для скачивания YouTube Shorts
def download_youtube_short(video_url, output_path='downloads'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        'format': 'best[height<=720][ext=mp4]',  # Скачивает лучшее видео до 720p
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'merge_output_format': 'mp4',
        'allow_unplayable_formats': False,
        'ignore_no_formats_error': False,
        'hls_prefer_native': True,
        'hls_use_mpegts': False,
        # Добавляем извлечение метаданных
        'writedescription': True,
        'writeinfojson': False,
        'writethumbnail': False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_filename = ydl.prepare_filename(info_dict)

            # Проверяем, что файл существует
            if not os.path.exists(video_filename):
                base, ext = os.path.splitext(video_filename)
                # Попробуем найти файл с другим расширением
                for possible_ext in ['.mp4', '.mkv', '.webm']:
                    if os.path.exists(base + possible_ext):
                        return base + possible_ext, info_dict
                return None, None

            return video_filename, info_dict
    except Exception as e:
        print(f"Ошибка при скачивании видео: {e}")
        return None, None


# Функция для скачивания TikTok видео
def download_tiktok_video(video_url, output_path='downloads'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=mp4]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'merge_output_format': 'mp4',
        # Добавляем извлечение метаданных
        'writedescription': True,
        'writeinfojson': False,
        'writethumbnail': False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_filename = ydl.prepare_filename(info_dict)

            if not os.path.exists(video_filename):
                base, ext = os.path.splitext(video_filename)
                for possible_ext in ['.mp4', '.mkv', '.webm']:
                    if os.path.exists(base + possible_ext):
                        return base + possible_ext, info_dict
                return None, None

            return video_filename, info_dict
    except Exception as e:
        print(f"Ошибка при скачивании TikTok видео: {e}")
        return None, None


# Запуск бота
if __name__ == "__main__":
    bot.infinity_polling()

