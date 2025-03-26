import asyncio
import logging
import os
from aiogram import Router
from dotenv import load_dotenv
from aiogram.types import Message
from bot.upwork_api import get_jobs
from bot.openai_api import generate_cover_letter

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID"))

router = Router()

# Глобальные переменные для хранения фильтров и состояния
keywords = ["telegram", "bot", "node.js"]
min_budget = 100
job_type = ["fixed", "hourly"]
auto_submit = True  # Включена ли автоматическая подача

async def send_notification(bot, message: str):
    """Отправляет уведомление администратору."""
    await bot.send_message(ADMIN_ID, message)

async def process_jobs(bot):
    """Фоновый процесс для поиска и подачи заявок."""
    global keywords, min_budget, job_type, auto_submit
    while True:
        if auto_submit:
            jobs = get_jobs(keywords, min_budget, job_type)
            if jobs:
                for job in jobs:
                    job_id = job['node']['id']
                    job_title = job['node']['title']
                    job_description = job['node']['description']
                    job_url = job['node']['url']

                    cover_letter = generate_cover_letter(job_description)

                    # TODO: Добавить функцию для автоматической подачи заявки через Upwork API
                    # submit_application(job_id, cover_letter)

                    message = f"📩 На вакансию: {job_url}\n🚀 Был автоматически отправлен Cover Letter:\n---\n{cover_letter}\n---"
                    await send_notification(bot, message)
            else:
                logging.info("Нет подходящих вакансий.")
        else:
            logging.info("Автоподача приостановлена.")
        await asyncio.sleep(600)  # Проверка каждые 10 минут

# Функция для запуска процесса обработки вакансий
async def start_job_processing(bot):
    asyncio.create_task(process_jobs(bot))

@router.message(commands=["set_keywords"])
async def set_keywords_command(message: Message):
    """Устанавливает ключевые слова для поиска вакансий."""
    global keywords
    keywords = message.text.split()[1:]  # Получаем ключевые слова из сообщения
    await message.answer(f"Ключевые слова установлены: {keywords}")

@router.message(commands=["set_min_budget"])
async def set_min_budget_command(message: Message):
    """Устанавливает минимальный бюджет для поиска вакансий."""
    global min_budget
    try:
        min_budget = int(message.text.split()[1])  # Получаем минимальный бюджет из сообщения
        await message.answer(f"Минимальный бюджет установлен: {min_budget}")
    except ValueError:
        await message.answer("Некорректный формат бюджета. Используйте число.")

@router.message(commands=["set_job_type"])
async def set_job_type_command(message: Message):
    """Устанавливает тип проекта для поиска вакансий."""
    global job_type
    job_type = message.text.split()[1:]  # Получаем тип проекта из сообщения
    await message.answer(f"Тип проекта установлен: {job_type}")

@router.message(commands=["pause"])
async def pause_command(message: Message):
    """Приостанавливает автоподачу заявок."""
    global auto_submit
    auto_submit = False
    await message.answer("Автоподача приостановлена.")

@router.message(commands=["resume"])
async def resume_command(message: Message):
    """Возобновляет автоподачу заявок."""
    global auto_submit
    auto_submit = True
    await message.answer("Автоподача возобновлена.")