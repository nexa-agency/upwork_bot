import logging
from aiogram import Router, types
from aiogram.filters import Command

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    logger.info(f"Received /start command from user: {message.from_user.id}")
    await message.answer("Привет! Я бот для автоматической подачи заявок на Upwork.")

# Удаляем обработчик эхо-сообщений, чтобы он не перехватывал все команды
# @router.message()
# async def echo_handler(message: types.Message):
#     await message.answer("This is a placeholder for job-related commands.")
