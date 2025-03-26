import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import TELEGRAM_TOKEN
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.utils.db import create_db
from bot.handlers import commands, jobs  # Импортируем handlers

sys.path.append(os.getcwd())

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
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
        BotCommand(command="set_keywords", description="Установить ключевые слова"),
        BotCommand(command="set_min_budget", description="Установить минимальный бюджет"),
        BotCommand(command="set_job_type", description="Установить тип проекта"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Создаем таблицы в базе данных
    await create_db()

    # Установка команд бота
    await set_commands(bot)

    # Регистрация handlers
    dp.include_router(commands.router)
    dp.include_router(jobs.router)

    # Запуск процесса обработки вакансий
    asyncio.create_task(jobs.process_jobs(bot))

    # Запуск polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())