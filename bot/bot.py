import asyncio
import os
import sys
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, DefaultBotProperties  # Import DefaultBotProperties

from config import TELEGRAM_TOKEN, OPENAI_API_KEY, UPWORK_PUBLIC_KEY, UPWORK_SECRET_KEY, ADMIN_ID
# from bot.middlewares.throttling import ThrottlingMiddleware #
# from bot.utils.db import create_db, save_job, save_proposal #
from upwork_api import get_access_token, search_jobs, submit_proposal
from openai_api import generate_cover_letter  # Исправленный импорт
from filters import filter_jobs
from models import Job, Proposal

sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))  # Use DefaultBotProperties
dp = Dispatcher()

# Регистрация middlewares
# dp.message.middleware(ThrottlingMiddleware(limit=1))

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
    # await create_db()

    # Установка команд бота
    await set_commands(bot)

    # Регистрация handlers
    # dp.include_router(bot.handlers.commands.router)
    # dp.include_router(bot.handlers.jobs.router)

    # Get Upwork access token
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to obtain Upwork access token.")
        return

    # Example usage: Search for jobs and submit proposals
    search_query = "Python developer"
    jobs = search_jobs(search_query)

    if jobs:
        logger.info(f"Found {len(jobs)} jobs.")
        for job_data in jobs:
            try:
                job = Job(
                    id=job_data['id'],
                    title=job_data['title'],
                    description=job_data['snippet'],
                    url=f"https://www.upwork.com/jobs/{job_data['id']}",
                    budget=job_data['budget']['amount'],
                    skills=[skill['name'] for skill in job_data['skills']],
                    proposals=""  # Добавлено значение по умолчанию
                )

                # Save job to database
                # save_job(job)

                # Generate cover letter
                cover_letter = generate_cover_letter(job.description)
                if cover_letter:
                    # Submit proposal
                    if submit_proposal(job.id, cover_letter):
                        logger.info(f"Successfully submitted proposal to job ID: {job.id}")
                        # Save proposal to database
                        # save_proposal(job.id, cover_letter, "submitted")
                    else:
                        logger.error(f"Failed to submit proposal to job ID: {job.id}")
                else:
                    logger.warning(f"Failed to generate cover letter for job ID: {job.id}")

            except Exception as e:
                logger.exception(f"Error processing job ID: {job_data['id']}")
    else:
        logger.info("No jobs found.")

    # Запуск polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())