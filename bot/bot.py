import asyncio
import logging
import os
import sys
import openai
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import (
    BotCommand,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.client.default import DefaultBotProperties

from middlewares.throttling import ThrottlingMiddleware
# from utils.db import create_db
from config import TELEGRAM_TOKEN
from handlers import commands, jobs  # Corrected import

sys.path.append(os.getcwd())

# Установите ваш OpenAI API ключ
openai.api_key = "YOUR_OPENAI_API_KEY"

# Промт для генерации текста поста
POST_PROMPT = """
Generate a professional LinkedIn post for a software development team. The post should highlight the team's expertise in full-cycle product development, Web3, SaaS, and automation solutions. Include benefits of working with the team, such as cost-effectiveness, scalability, and tailored solutions for startups. Use a professional and engaging tone.
"""

# Промт для генерации изображения
IMAGE_PROMPT = (
    "Futuristic 3D illustration of floating glossy geometric shapes (discs, cylinders, torus) "
    "with soft translucent materials, iridescent blue gradients, neon rim lighting, and a glowing "
    "purple-blue gradient background. Clean, minimal, abstract composition with depth and reflections, modern digital art style."
)

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


# Функция для генерации текста поста через OpenAI API
async def generate_post_text():
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=POST_PROMPT, max_tokens=300, temperature=0.7
    )
    return response["choices"][0]["text"].strip()


# Функция для генерации изображения через OpenAI API
async def generate_image():
    response = openai.Image.create(prompt=IMAGE_PROMPT, n=1, size="1920x720")
    return response["data"][0]["url"]


# Функция для отправки поста
async def send_post(chat_id: int, bot: Bot):
    post_text = await generate_post_text()
    image_url = await generate_image()
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔄 Перегенерировать", callback_data="regenerate_post")
    )
    await bot.send_photo(
        chat_id=chat_id,
        photo=image_url,
        caption=post_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )


# Обработчик команды /generate_post
@dp.message(commands=["generate_post"])
async def handle_generate_post(message: Message):
    await send_post(message.chat.id, bot)


# Обработчик кнопки "Перегенерировать"
@dp.callback_query(lambda c: c.data == "regenerate_post")
async def handle_regenerate_post(callback_query: types.CallbackQuery):
    await send_post(callback_query.message.chat.id, bot)
    await callback_query.answer()


# Планировщик для ежедневной генерации
scheduler = AsyncIOScheduler()


async def daily_post():
    chat_id = "YOUR_BOT_CHAT_ID"  # Укажите ID чата бота
    await send_post(chat_id, bot)


# Запуск планировщика
scheduler.add_job(daily_post, "cron", hour=9)  # Генерация поста каждый день в 9 утра
scheduler.start()


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
