import json
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import config

API_TOKEN = config.token
YOUR_CHAT_ID = config.tg_id
DATA_FILE = 'user_data.json'

# Инициализируем бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Словарь для хранения ID чата пользователей по их тегам
user_ids = {}

def load_user_ids():
    global user_ids
    try:
        with open(DATA_FILE, 'r') as file:
            user_ids = json.load(file)
    except FileNotFoundError:
        user_ids = {}

def save_user_ids():
    with open(DATA_FILE, 'w') as file:
        json.dump(user_ids, file)

@dp.message(Command('start'))
async def send_welcome(message: Message):
    user_tag = f"@{message.from_user.username}" if message.from_user.username else "Анонимный пользователь"
    if str(message.chat.id) == YOUR_CHAT_ID:
        await message.answer("Здравствуйте Камалиддин! Ждите новые собщения от пользователей")
    else:
        await message.answer("Отправьте свое сообщение")
        user_ids[user_tag] = message.chat.id
        save_user_ids()
        await bot.send_message(YOUR_CHAT_ID, f"{user_tag} запустил вашего бота!")
        print(f"Добавлено {user_tag} с айди чата {message.chat.id} в user_ids")

@dp.message()
async def process_message(message: Message):
    if str(message.chat.id) == YOUR_CHAT_ID:
        user_tag, _, reply_text = message.text.partition(' ')
        print(f"Отправленное сообщение создателя к : {message.text}")
        print(f"Текущие пользователи : {user_ids}")
        if user_tag in user_ids:
            await bot.send_message(user_ids[user_tag], reply_text)
            await message.answer(f"Ответ отправлен : {user_tag}")
        else:
            await message.answer(f"Тег пользователя {user_tag} не найден!")
    else:
        user_tag = f"@{message.from_user.username}" if message.from_user.username else "Анонимный пользователь"
        await bot.send_message(YOUR_CHAT_ID, f"{user_tag} : {message.text}")
        await message.answer("Отправлено!")
        print(f"Отправлено сообщение с {user_tag} создателю")

async def main():
    load_user_ids()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
