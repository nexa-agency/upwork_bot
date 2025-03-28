import asyncio
import json
import os
import urllib.parse

from aiogram import types, Router
from aiogram.filters import Command
import requests
from dotenv import load_dotenv

router = Router()

# Загружаем переменные окружения из файла .env
load_dotenv()

UPWORK_API_URL = "https://www.upwork.com/api/graphql"
UPWORK_CLIENT_ID = os.getenv("UPWORK_PUBLIC_KEY")  # Используем UPWORK_PUBLIC_KEY как client_id
UPWORK_CLIENT_SECRET = os.getenv("UPWORK_SECRET_KEY")  # Используем UPWORK_SECRET_KEY как client_secret
UPWORK_REDIRECT_URI = "https://example.com/callback"  # Замените на ваш redirect URI

# URL для получения authorization code
UPWORK_AUTHORIZE_URL = "https://www.upwork.com/ab/account-security/oauth2/authorize"

# URL для получения access token
UPWORK_TOKEN_URL = "https://www.upwork.com/api/v3/oauth2/token"

@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот для автоматической подачи заявок на Upwork.")

@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/filters - Настроить фильтры\n"
        "/pause - Приостановить автоподачу\n"
        "/resume - Возобновить автоподачу\n"
        "/test_upwork - Проверить подключение к Upwork API"
    )

@router.message(Command("filters"))
async def filters_command(message: types.Message):
    await message.answer("Здесь будут настройки фильтров.")

@router.message(Command("test_upwork"))
async def test_upwork_command(message: types.Message):
    """
    Эта команда тестирует подключение к Upwork API.
    """
    if not UPWORK_CLIENT_ID or not UPWORK_CLIENT_SECRET:
        await message.answer("Ошибка: Не установлены UPWORK_PUBLIC_KEY или UPWORK_SECRET_KEY в переменных окружения.")
        return

    # 1. Получение authorization code
    redirect_uri = urllib.parse.quote(UPWORK_REDIRECT_URI)
    authorize_url = f"{UPWORK_AUTHORIZE_URL}?response_type=code&client_id={UPWORK_CLIENT_ID}&redirect_uri={redirect_uri}"

    # Выводим URL авторизации для отладки
    print(f"Authorize URL: {authorize_url}")

    await message.answer(
        "Для начала, пожалуйста, авторизуйте приложение, перейдя по следующей ссылке:\n"
        f"{authorize_url}"
    )

    # Инструкция для пользователя
    await message.answer(
        "После авторизации, Upwork перенаправит вас на указанный вами redirect URI с authorization code в параметре `code`.\n"
        "Скопируйте этот authorization code и отправьте его мне командой `/code YOUR_AUTHORIZATION_CODE`."
    )

@router.message(Command("code"))
async def code_command(message: types.Message):
    """
    Эта команда получает authorization code от пользователя и обменивает его на access token.
    """
    authorization_code = message.text.split(" ")[1]  # Получаем authorization code из сообщения

    if not authorization_code:
        await message.answer("Ошибка: Пожалуйста, укажите authorization code после команды `/code`.")
        return

    # 2. Получение access token
    data = {
        "grant_type": "authorization_code",
        "client_id": UPWORK_CLIENT_ID,
        "client_secret": UPWORK_CLIENT_SECRET,
        "code": authorization_code,
        "redirect_uri": UPWORK_REDIRECT_URI,
    }

    try:
        response = requests.post(UPWORK_TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            await message.answer(f"Ошибка при получении access token: {token_data.get('error_description') or token_data.get('error') or 'Неизвестная ошибка'}")
            return

        # Сохраняем access_token (временно в памяти)
        global ACCESS_TOKEN
        ACCESS_TOKEN = access_token

        await message.answer("Access token успешно получен! Теперь вы можете использовать команду `/me` для получения информации о вашем профиле.")

    except requests.exceptions.RequestException as e:
        await message.answer(f"Ошибка при запросе access token: {e}")
    except json.JSONDecodeError as e:
        await message.answer(f"Ошибка разбора JSON ответа: {e}\nОтвет: {response.text}")
    except Exception as e:
        await message.answer(f"Неизвестная ошибка: {e}")

@router.message(Command("me"))
async def me_command(message: types.Message):
    """
    Эта команда получает информацию о профиле пользователя.
    """
    # Проверяем, есть ли access token
    if not ACCESS_TOKEN:
        await message.answer("Ошибка: Сначала необходимо получить access token, выполнив команду `/test_upwork` и `/code`.")
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        # "X-Upwork-API-TenantId": "YOUR_ORGANIZATION_ID",  # Замените на ваш Organization ID
    }

    query = """
    query {
      me {
        id
        firstName
        lastName
        profileUrl
      }
    }
    """

    try:
        response = requests.post(
            UPWORK_API_URL,
            headers=headers,
            json={"query": query},
            timeout=10
        )
        response.raise_for_status()

        result = response.json()

        if result.get("data") and result["data"].get("me"):
            user_info = result["data"]["me"]
            await message.answer(
                f"Информация о профиле:\n"
                f"ID: {user_info['id']}\n"
                f"Имя: {user_info['firstName']}\n"
                f"Фамилия: {user_info['lastName']}\n"
                f"Профиль: {user_info['profileUrl']}"
            )
        else:
            await message.answer(f"Ошибка при получении данных из Upwork API: {result.get('errors')}")

    except requests.exceptions.RequestException as e:
        await message.answer(f"Ошибка подключения к Upwork API: {e}")
    except json.JSONDecodeError as e:
        await message.answer(f"Ошибка разбора JSON ответа: {e}\nОтвет: {response.text}")
    except Exception as e:
        await message.answer(f"Неизвестная ошибка: {e}")

# Глобальная переменная для хранения access token (ВНИМАНИЕ: это небезопасно для production)
ACCESS_TOKEN = None