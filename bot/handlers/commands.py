from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот для автоматической подачи заявок на Upwork.")

@router.message(commands=["help"])
async def help_command(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/filters - Настроить фильтры\n"
        "/pause - Приостановить автоподачу\n"
        "/resume - Возобновить автоподачу"
    )

@router.message(commands=["filters"])
async def filters_command(message: types.Message):
    await message.answer("Здесь будут настройки фильтров.")

@router.message(commands=["pause"])
async def pause_command(message: types.Message):
    await message.answer("Автоподача приостановлена.")

@router.message(commands=["resume"])
async def resume_command(message: types.Message):
    await message.answer("Автоподача возобновлена.")