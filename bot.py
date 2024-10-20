import asyncio
import aiosqlite
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import API_TOKEN
from handlers import start, admin_kb, service_kb
from middleware import AdminCheckMiddleware


async def set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Начать работу")
    ]
    await bot.set_my_commands(commands)

# Инициализация БД
async def init_db() -> None:
    async with aiosqlite.connect("database.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        await db.commit()

async def main() -> None:
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # Подключаем промежуточное ПО для проверки прав администратора
    dp.message.middleware(AdminCheckMiddleware())
    dp.callback_query.middleware(AdminCheckMiddleware())

    dp.include_router(start.router)
    dp.include_router(admin_kb.router)
    dp.include_router(service_kb.router)
    await init_db()
    await bot.delete_webhook(True)
    await set_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())