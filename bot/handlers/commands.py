from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class FilterState(StatesGroup):
    keywords = State()
    min_budget = State()
    project_types = State()

@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Я бот для автоматической подачи заявок на Upwork.\nИспользуйте /help для списка команд.")

@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/filters - Настроить фильтры\n"
        "/pause - Приостановить автоподачу\n"
        "/resume - Возобновить автоподачу"
    )

@router.message(Command("filters"))
async def filters_command(message: types.Message, state: FSMContext):
    await state.set_state(FilterState.keywords)
    await message.answer("Введите ключевые слова для фильтрации вакансий (через запятую):")

@router.message(FilterState.keywords)
async def process_keywords(message: types.Message, state: FSMContext):
    keywords = [keyword.strip() for keyword in message.text.split(",")]
    await state.update_data(keywords=keywords)
    await state.set_state(FilterState.min_budget)
    await message.answer("Введите минимальную ставку для вакансий:")

@router.message(FilterState.min_budget)
async def process_min_budget(message: types.Message, state: FSMContext):
    try:
        min_budget = float(message.text)
        await state.update_data(min_budget=min_budget)
        await state.set_state(FilterState.project_types)
        await message.answer("Введите типы проектов (fixed, hourly, через запятую):")
    except ValueError:
        await message.answer("Некорректный формат. Введите число.")
        return

@router.message(FilterState.project_types)
async def process_project_types(message: types.Message, state: FSMContext):
    project_types = [project_type.strip() for project_type in message.text.split(",")]
    await state.update_data(project_types=project_types)
    data = await state.get_data()
    await state.clear()
    await message.answer(f"Фильтры установлены:\nКлючевые слова: {data['keywords']}\nМинимальная ставка: {data['min_budget']}\nТипы проектов: {data['project_types']}")

# Add handlers for pause and resume commands
@router.message(Command("pause"))
async def pause_command(message: types.Message):
    # Implement logic to pause the bot
    await message.answer("Автоматическая подача заявок приостановлена.")

@router.message(Command("resume"))
async def resume_command(message: types.Message):
    # Implement logic to resume the bot
    await message.answer("Автоматическая подача заявок возобновлена.")