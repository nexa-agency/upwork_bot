import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPWORK_PUBLIC_KEY = os.getenv("UPWORK_PUBLIC_KEY")
UPWORK_SECRET_KEY = os.getenv("UPWORK_SECRET_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")

DEFAULT_KEYWORDS = ["telegram", "bot", "node.js"]
DEFAULT_MIN_BUDGET = 100
DEFAULT_PROJECT_TYPES = ["fixed", "hourly"]