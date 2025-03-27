import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties

from middlewares.throttling import ThrottlingMiddleware
from utils.db import create_db
from config import TELEGRAM_TOKEN
from handlers import commands, jobs  # Corrected import

sys.path.append(os.getcwd())

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрация middlewares
dp.message.middleware(ThrottlingMiddleware(limit=1))

# Регистрация handlers
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="filters", description="Настроить фильтры"),
        BotCommand(command="pause", description="Приостановить автоподачу"),
        BotCommand(command="resume", description="Возобновить автоподачу"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Создаем таблицы в базе данных
    await create_db()

    # Установка команд бота
    await set_commands(bot)

    # Регистрация handlers
    dp.include_router(commands.router)  # Corrected usage
    dp.include_router(jobs.router)  # Removed line

    # Запуск polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())