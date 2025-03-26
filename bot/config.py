import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPWORK_TOKEN = os.getenv("UPWORK_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Преобразуем в целое число
DATABASE_URL = os.getenv("DATABASE_URL")

# Фильтры по умолчанию
DEFAULT_KEYWORDS = ["telegram", "bot", "node.js"]
DEFAULT_MIN_BUDGET = 100
DEFAULT_PROJECT_TYPES = ["fixed", "hourly"]