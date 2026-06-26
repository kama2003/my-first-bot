import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message

# Загружаем токен из файла .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Создаём объект бота и диспетчер (он распределяет входящие сообщения по функциям)
bot = Bot(token=TOKEN)
dp = Dispatcher()


# Эта функция сработает, когда пользователь отправит команду /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Я твой первый бот. Напиши мне что-нибудь, и я повторю это."
    )


# Эта функция сработает на ЛЮБОЕ другое текстовое сообщение
@dp.message()
async def echo(message: Message):
    await message.answer(f"Ты написал: {message.text}")


# Главная функция запуска бота
async def main():
    print("Бот запущен. Нажми Ctrl+C чтобы остановить.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())