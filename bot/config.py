import os
import aiogram

# Получаем переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPWORK_PUBLIC_KEY = os.getenv("UPWORK_PUBLIC_KEY")
UPWORK_SECRET_KEY = os.getenv("UPWORK_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверяем наличие ADMIN_ID
ADMIN_ID = os.getenv("ADMIN_ID")
if ADMIN_ID is None:
    raise ValueError("Переменная окружения ADMIN_ID не установлена. Убедитесь, что она добавлена в Config Vars на Heroku.")
try:
    ADMIN_ID = int(ADMIN_ID)  # Преобразуем в целое число
except ValueError:
    raise ValueError("Переменная ADMIN_ID должна быть числом.")

# Фильтры по умолчанию
DEFAULT_KEYWORDS = ["telegram", "bot", "node.js"]
DEFAULT_MIN_BUDGET = 100
DEFAULT_PROJECT_TYPES = ["fixed", "hourly"]

