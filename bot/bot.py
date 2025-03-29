import asyncio
import logging
import os
import openai
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

from middlewares.throttling import ThrottlingMiddleware
from config import TELEGRAM_TOKEN
from handlers.commands import router as commands_router
from handlers.jobs import router as jobs_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Register middleware
dp.message.middleware(ThrottlingMiddleware(limit=1))

# Register routers
dp.include_router(commands_router)
dp.include_router(jobs_router)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompts for OpenAI
POST_PROMPT = """
Generate a professional LinkedIn post for a software development team. The post should highlight the team's expertise in full-cycle product development, Web3, SaaS, and automation solutions. Include benefits of working with the team, such as cost-effectiveness, scalability, and tailored solutions for startups. Use a professional and engaging tone.
"""

IMAGE_PROMPT = """
Futuristic 3D illustration of floating glossy geometric shapes (discs, cylinders, torus) with soft translucent materials, iridescent blue gradients, neon rim lighting, and a glowing purple-blue gradient background. Clean, minimal, abstract composition with depth and reflections, modern digital art style.
"""

# Function to generate post text
async def generate_post_text():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional assistant for generating LinkedIn posts."},
            {"role": "user", "content": POST_PROMPT},
        ],
        max_tokens=300,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

# Function to generate image
async def generate_image():
    response = client.images.generate(
        model="dall-e-3",
        prompt=IMAGE_PROMPT,
        n=1,
        size="1920x1080"
    )
    return response.data[0].url

# Function to send post
async def send_post(chat_id: int, bot: Bot):
    post_text = await generate_post_text()
    image_url = await generate_image()
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔄 Regenerate", callback_data="regenerate_post")
    )
    await bot.send_photo(
        chat_id=chat_id,
        photo=image_url,
        caption=post_text,
        reply_markup=keyboard,
    )

# Handler for /generate_post command
async def handle_generate_post(message: Message):
    await send_post(message.chat.id, bot)

# Handler for "Regenerate" button
async def handle_regenerate_post(callback_query: types.CallbackQuery):
    await send_post(callback_query.message.chat.id, bot)
    await callback_query.answer()

# Register handlers
dp.message.register(handle_generate_post, Command("generate_post"))
dp.callback_query.register(handle_regenerate_post, lambda c: c.data == "regenerate_post")

# Scheduler for daily posts
scheduler = AsyncIOScheduler()

async def daily_post():
    chat_id = int(os.getenv("BOT_CHAT_ID"))  # Ensure BOT_CHAT_ID is set in Heroku Config Vars
    await send_post(chat_id, bot)

scheduler.add_job(daily_post, "cron", hour=9)  # Schedule daily post at 9 AM

# Main function
async def main():
    # Set bot commands
    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Help"),
        BotCommand(command="generate_post", description="Generate a post"),
    ])

    # Start the scheduler
    scheduler.start()

    # Start polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

# Additional router for start and help commands
router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    logger.info(f"Received /start command from user: {message.from_user.id}")
    await message.answer("Привет! Я бот для автоматической подачи заявок на Upwork.")

@router.message(Command("help"))
async def help_command(message: types.Message):
    logger.info(f"Received /help command from user: {message.from_user.id}")
    await message.answer(
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/generate_post - Сгенерировать пост"
    )

dp.include_router(router)
