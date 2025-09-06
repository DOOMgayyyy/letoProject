import logging
import random
import os
import json
import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загружаем переменные окружения из .env файла
load_dotenv()

# --- Конфигурация ---
# Токен бота из переменной окружения для безопасности.
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Инициализация бота и диспетчера ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Фразы для ответов ---
MENTION_REPLIES = [
    "Кто-то звал самого веселого бота? 🎉",
    "На месте! Готов шутить и смеяться. 😄",
    "Вы упомянули меня! У вас отличный вкус. ✨",
    "Я здесь! Что-то случилось или просто хотели поболтать?",
    "Слышу-слышу! Чем могу быть полезен?",
]

JOKE_KEYWORDS = ["анекдот", "шутка", "шутку", "расскажи", "пошути", "joke"]

# --- Работа с JSON-файлом ---

def load_jokes_from_json(file_path='jokes.json'):
    """Загружает анекдоты из JSON-файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Файл '{file_path}' не найден. Бот не сможет рассказывать анекдоты. Запустите parser.py")
        return []
    except json.JSONDecodeError:
        logging.error(f"Ошибка чтения JSON из файла '{file_path}'. Файл может быть поврежден.")
        return []

# Сразу загружаем все анекдоты в память при старте
jokes_list = load_jokes_from_json()

def get_random_joke():
    """Возвращает случайный анекдот из списка."""
    if jokes_list:
        return random.choice(jokes_list).get("text")
    # Возвращаем None, если список анекдотов пуст
    return None

# --- Обработчики команд и сообщений ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    start_message = (
        "<b>Привет! Я бот-весельчак!</b>\n\n"
        "Добавьте меня в свой групповой чат, и я буду рассказывать анекдоты!\n\n"
        "<b>Как мной пользоваться:</b>\n"
        "• Напишите команду <code>/joke</code>, чтобы получить случайный анекдот.\n"
        "• Упомяните меня (@имя_бота) и попросите рассказать шутку, например: "
        "<i>«@имя_бота, расскажи анекдот»</i>.\n"
        "• Если просто упомянуть меня, я тоже отреагирую! 😉"
    )
    await message.answer(start_message)

@dp.message(Command("joke"))
async def cmd_joke(message: types.Message):
    """Обработчик команды /joke."""
    # Получаем анекдот напрямую из функции для JSON
    joke_text = get_random_joke()
    if joke_text:
        await message.answer(joke_text)
    else:
        await message.answer("Упс, у меня закончились шутки! 😔 Запустите парсер или проверьте файл `jokes.json`.")

@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_messages(message: types.Message):
    """
    Главный обработчик сообщений в группах.
    Реагирует на упоминание бота.
    """
    if not message.text:
        return

    bot_info = await bot.get_me()
    bot_username = bot_info.username

    if f"@{bot_username}".lower() in message.text.lower():
        text_lower = message.text.lower()
        if any(keyword in text_lower for keyword in JOKE_KEYWORDS):
            # Получаем анекдот напрямую из функции для JSON
            joke_text = get_random_joke()
            if joke_text:
                await message.reply(joke_text)
            else:
                await message.reply("Хотел бы пошутить, но шутки кончились! 😥")
        else:
            reply_phrase = random.choice(MENTION_REPLIES)
            await message.reply(reply_phrase)


# --- Функция для запуска бота ---
async def main():
    """Основная функция для запуска бота."""
    logging.info("Бот запускается...")
    # Просто запускаем опрос, без инициализации БД
    await dp.start_polling(bot)


if __name__ == '__main__':
    if not BOT_TOKEN:
        logging.critical("Токен бота не найден! Укажите BOT_TOKEN в .env файле.")
    else:
        asyncio.run(main())