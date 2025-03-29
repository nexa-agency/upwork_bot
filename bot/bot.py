import asyncio
import logging
from mailbox import Message
import os
import openai
import aiohttp
from bs4 import BeautifulSoup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram import Router

from middlewares.throttling import ThrottlingMiddleware
from config import TELEGRAM_TOKEN

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=openai.BaseModel.HTML)
)
dp = Dispatcher()

# Register middleware
dp.message.middleware(ThrottlingMiddleware(limit=1))

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompts for OpenAI
POST_PROMPT = """
Generate a professional LinkedIn post for a software development team. The post should highlight the team's expertise in full-cycle product development, Web3, SaaS, and automation solutions. Include benefits of working with the team, such as cost-effectiveness, scalability, and tailored solutions for startups. Use a professional and engaging tone.
"""

IMAGE_PROMPT = """
Futuristic 3D illustration of floating glossy geometric shapes (discs, cylinders, torus) with soft translucent materials, iridescent blue gradients, neon rim lighting, and a glowing blue gradient background. Clean, minimal, abstract composition with depth and reflections, modern digital art style.
"""

# Function to generate post text
async def generate_post_text():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional assistant for generating LinkedIn posts. Keep the post under 900 characters."},
            {"role": "user", "content": POST_PROMPT},
        ],
        max_tokens=200,  # Reduced from 300 to ensure shorter responses
        temperature=0.7,
    )
    text = response.choices[0].message.content.strip()
    # Ensure the text doesn't exceed Telegram's limit
    return text[:1024] if len(text) > 1024 else text

# Function to generate image
async def generate_image():
    response = client.images.generate(
        model="dall-e-3",
        prompt=IMAGE_PROMPT,
        n=1,
        size="1792x1024"
    )
    return response.data[0].url

from aiogram.types import InlineKeyboardMarkup

# Function to send post
async def send_post(chat_id: int, bot: Bot):
    try:
        post_text = await generate_post_text()
        image_url = await generate_image()
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                {"text": "🔄 Regenerate", "callback_data": "regenerate_post"}
            ]]
        )
        
        await bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption=post_text,
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.error(f"Error in send_post: {e}")
        await bot.send_message(chat_id=chat_id, text="Sorry, there was an error generating the post. Please try again.")

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

# Job search configuration
UPWORK_SEARCH_URL = "https://www.upwork.com/nx/search/jobs/?amount=500-&category2_uid=531770282580668418&client_hires=1-9,10-&from_recent_search=true&hourly_rate=10-&location=Americas,Europe&proposals=0-4,5-9,10-14,15-19&q=dev&sort=recency&t=0,1"

JOB_ANALYSIS_PROMPT = """
Analyze this job posting and provide:
1. Tech Stack Required
2. Project Scope
3. Pros of the job
4. Cons of the job
5. Required Experience
6. Budget/Rate
7. Should we apply? (Yes/No and brief explanation)

Keep the format clean without markdown formatting or special characters.
"""

COVER_LETTER_PROMPT = """
Write a compelling cover letter for this job posting. Consider:
1. Match requirements with our experience
2. Show understanding of the project
3. Address any specific questions
4. Highlight relevant experience
5. Keep it concise and professional
"""

# Store previously seen jobs
seen_jobs = set()

async def fetch_job_details(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        logger.error(f"Error fetching job details: {e}")
        return None

async def analyze_job(job_html):
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional job analyzer."},
                {"role": "user", "content": f"{JOB_ANALYSIS_PROMPT}\n\nJob Description:\n{job_html}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error analyzing job: {e}")
        return None

async def generate_cover_letter(job_html):
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer."},
                {"role": "user", "content": f"{COVER_LETTER_PROMPT}\n\nJob Description:\n{job_html}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        return None

async def check_new_jobs():
    async with aiohttp.ClientSession() as session:
        try:
            jobs_html = await fetch_job_details(session, UPWORK_SEARCH_URL)
            if not jobs_html:
                return
            
            soup = BeautifulSoup(jobs_html, 'html.parser')
            new_jobs = soup.find_all('div', class_='job-tile')  # Adjust class based on actual Upwork HTML
            
            for job in new_jobs:
                job_id = job.get('data-job-id')  # Adjust based on actual HTML structure
                if job_id not in seen_jobs:
                    seen_jobs.add(job_id)
                    
                    job_url = f"https://www.upwork.com/jobs/{job_id}"  # Adjust URL format
                    job_details = await fetch_job_details(session, job_url)
                    analysis = await analyze_job(job_details)
                    
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(text="Write Cover Letter", callback_data=f"cover_{job_id}"),
                                InlineKeyboardButton(text="Reject", callback_data=f"reject_{job_id}")
                            ],
                            [InlineKeyboardButton(text="Apply Now", url=job_url)]
                        ]
                    )
                    
                    await bot.send_message(
                        chat_id=int(os.getenv("BOT_CHAT_ID")),
                        text=f"New Job Found!\n\n{analysis}\n\nJob Link: {job_url}",
                        reply_markup=keyboard
                    )
                    
        except Exception as e:
            logger.error(f"Error checking new jobs: {e}")

# Callback handler for cover letter generation
async def handle_cover_letter(callback_query: types.CallbackQuery):
    job_id = callback_query.data.split('_')[1]
    job_url = f"https://www.upwork.com/jobs/{job_id}"  # Adjust URL format
    
    async with aiohttp.ClientSession() as session:
        job_details = await fetch_job_details(session, job_url)
        cover_letter = await generate_cover_letter(job_details)
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Apply Now", url=job_url)]]
        )
        
        await callback_query.message.reply(
            text=f"Here's your cover letter:\n\n{cover_letter}",
            reply_markup=keyboard
        )
    await callback_query.answer()

# Register handlers
dp.callback_query.register(handle_cover_letter, lambda c: c.data.startswith("cover_"))

# Schedule job checks
scheduler = AsyncIOScheduler()
scheduler.add_job(check_new_jobs, 'interval', minutes=30)

# Main function
async def main():
    # Set bot commands
    await bot.set_my_commands([
        Command(command="start", description="Start the bot"),
        Command(command="help", description="Help"),
        Command(command="generate_post", description="Generate a post"),
        BotCommand(command="check_jobs", description="Check for new jobs now"), # type: ignore # type: ignore
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

@dp.message(Command("check_jobs"))
async def check_jobs_command(message: types.Message):
    """Manually trigger job checking."""
    await message.answer("Проверяю новые вакансии на Upwork...")
    await check_new_jobs()
    await message.answer("Проверка завершена.")