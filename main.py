import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import BOT_TOKEN
from database.db import init_db, async_session_maker
from handlers import common, calculate, settings, history

logging.basicConfig(level=logging.INFO)


async def db_middleware(handler, event, data):
    async with async_session_maker() as session:
        data["session"] = session
        return await handler(event, data)


async def main():
    await init_db()

    session = AiohttpSession(proxy="http://127.0.0.1:12334")
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(db_middleware)

    dp.include_router(common.router)
    dp.include_router(calculate.router)
    dp.include_router(settings.router)
    dp.include_router(history.router)

    logging.info("Бот запущен.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
