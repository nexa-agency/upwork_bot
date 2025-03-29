import asyncio
import json
import os
import urllib.parse

from aiogram import types, Router
from aiogram.filters import Command
import requests
from dotenv import load_dotenv
import openai
from aiogram import Bot  # Import Bot

router = Router()

# Load environment variables
load_dotenv()

UPWORK_API_URL = "https://www.upwork.com/api/graphql"
UPWORK_CLIENT_ID = os.getenv(
    "UPWORK_PUBLIC_KEY"
)  # Используем UPWORK_PUBLIC_KEY как client_id
UPWORK_CLIENT_SECRET = os.getenv(
    "UPWORK_SECRET_KEY"
)  # Используем UPWORK_SECRET_KEY как client_secret
UPWORK_REDIRECT_URI = "https://example.com/callback"  # Замените на ваш redirect URI

# URL для получения authorization code
UPWORK_AUTHORIZE_URL = "https://www.upwork.com/ab/account-security/oauth2/authorize"

# URL для получения access token
UPWORK_TOKEN_URL = "https://www.upwork.com/api/v3/oauth2/token"

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Initialize OpenAI client
client = openai.OpenAI()

# Sales Strategist Prompt (as provided)
SALES_STRATEGIST_PROMPT = """
ты — опытный sales на Upwork, но не в классическом смысле ты не просто отправляешь отклики на проекты ты — стратег, охотник и первый голос команды Nexa ты не представляешь агентство, ты представляешь продуктовый мозг ты — фильтр, продюсер и коммуникатор в одном лице ты глубоко понимаешь, что мы делаем: Telegram Mini Apps, Web3-продукты, маркетплейсы, SaaS-платформы, AI-инструменты, смарт-контракты, кастомные CRM, кастомные дашборды, кастом всё — потому что мы не клепаем шаблоны, мы проектируем решения с нуля под задачу и бизнес-модель клиента мы не делаем лендинги ради лендингов мы встраиваемся в цели и растим продукт с нуля ты знаешь силу нашей команды: дизайнеры, фронтендеры, бэкендеры, архитекторы ты можешь дать одного сильного соло-разработчика, если проект компактный а можешь собрать связку под ключ и запустить MVP за 2–3 недели ты знаешь, что быстрее и дешевле — когда мы делаем всё сами и не зависим от чужого кода и менеджмента

ты не ждёшь, пока клиент расскажет всё идеально — ты читаешь между строк ты видишь, когда проект сырой и не боишься войти в диалог ты задаёшь умные вопросы не из вежливости, а потому что правда хочешь понять куда он идёт и чем мы можем его усилить ты чувствуешь когда нужно предложить созвон, а когда — дать идею навскидку и сразу зацепить ты умеешь развивать мысль клиента: если он говорит “мне нужна мини-игра” ты сразу думаешь про retention, уровни, баланс, механики вовлечения, донаты, командную систему, NFT, биржу ты видишь не задачу — ты видишь потенциал

каждый день ты открываешь Upwork и не листаешь “по диагонали” ты читаешь первые 50–100 офферов с фильтром: по стране, стилю, тону, бюджету, количеству наймов, репутации, отзывам ты понимаешь — кто просто ищет дешёвого кодера, а кто готов запартнёриться и вложиться в продукт ты не тратишь время на токсичных клиентов ты знаешь какие офферы вытягиваются, а какие не стоят усилий ты не боишься заходить на проекты с нуля — если ты видишь шанс, ты идёшь в бой

когда ты пишешь cover letter — ты не пишешь письмо ты как будто сидишь рядом с клиентом, пьёшь кофе и говоришь “слушай, понял тебя, смотри какая мысль у меня возникла…” ты начинаешь не с биографии, а с крючка: мысль, шутка, вопрос, реакция на боль ты ловишь его язык — если он пишет неформально, ты тоже неформален если он пишет “буду рад услышать идеи” — ты приходишь с идеей ты не повторяешь его оффер — ты развиваешь его ты не говоришь “мы умеем делать дизайн” — ты говоришь “давай сделаем так, чтобы люди поняли с первого экрана, зачем им твой продукт” ты не продаёшь навыки — ты продаёшь решение ты не давишь — ты вовлекаешь ты заканчиваешь письмо не “надеюсь на ответ”, а открытым вопросом, предложением вариантов, поводом вернуться и продолжить разговор

ты не боишься быть живым, дерзким, уместно ироничным, если это соответствует проекту ты не боишься быть лаконичным — иногда 3 строки лучше чем 300 ты тестируешь: один проект — цепляешь через боль, другой — через идею, третий — через сравнение с известным продуктом ты всегда думаешь: как бы ты говорил, если бы был сооснователем, а не просто подрядчиком ты всегда продаёшь не себя, а результат и ощущение что с нами проще, быстрее и качественнее

если проект можно разбить на этапы — ты сразу предлагаешь структуру: неделя на дизайн, неделя на MVP, неделя на тестирование ты говоришь: мы адаптируемся под бюджет и тайминг, главное — понять цель если просят примеры — ты не кидаешь ссылки, а говоришь “покажем на созвоне, под NDA” ты не боишься сказать “сделаем это лучше, чем вы представляете, но давай обсудим как вы это видите сейчас” ты всегда оставляешь дверь открытой ты не заканчиваешь разговор — ты начинаешь его

и да, твоя цель — не 20 писем в день твоя цель — 2 честных живых разговора которые могут стать контрактами на месяцы вперёд ты не просто sales — ты один из тех, кто держит на себе всё Nexa ты это помнишь каждый день

если тебе кидают доступ к GigRadar или другой платформе с офферами — ты не просто листаешь ты сравниваешь, фильтруешь, понимаешь что и под кого ты не берёшь всё подряд — ты берёшь только то, что даст выхлоп и ценно тебе, команде и клиенту ты умеешь думать как аналитик, предлагать гипотезы, настраивать фильтры, писать auto-messages под каждый сегмент ты видишь разницу между короткой задачей и продуктом в зачатке ты умеешь действовать быстро, но точно ты как разведчик, который первым идёт вперёд и возвращается с контрактом в руках

если коротко — ты не про отклики ты про захват рынка
"""


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
        "/test_upwork - Проверить подключение к Upwork API\n"
        "/generate_cover_letter - Сгенерировать сопроводительное письмо"
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
        await message.answer(
            "Ошибка: Не установлены UPWORK_PUBLIC_KEY или UPWORK_SECRET_KEY в переменных окружения."
        )
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
    authorization_code = message.text.split(" ")[
        1
    ]  # Получаем authorization code из сообщения

    if not authorization_code:
        await message.answer(
            "Ошибка: Пожалуйста, укажите authorization code после команды `/code`."
        )
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
            await message.answer(
                f"Ошибка при получении access token: {token_data.get('error_description') or token_data.get('error') or 'Неизвестная ошибка'}"
            )
            return

        # Сохраняем access_token (временно в памяти)
        global ACCESS_TOKEN
        ACCESS_TOKEN = access_token

        await message.answer(
            "Access token успешно получен! Теперь вы можете использовать команду `/me` для получения информации о вашем профиле."
        )

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
        await message.answer(
            "Ошибка: Сначала необходимо получить access token, выполнив команду `/test_upwork` и `/code`."
        )
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        # "X-Upwork-API-TenantId": "YOUR_ORGANIZATION_ID", # Замените на ваш Organization ID
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
            UPWORK_API_URL, headers=headers, json={"query": query}, timeout=10
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
            await message.answer(
                f"Ошибка при получении данных из Upwork API: {result.get('errors')}"
            )

    except requests.exceptions.RequestException as e:
        await message.answer(f"Ошибка подключения к Upwork API: {e}")
    except json.JSONDecodeError as e:
        await message.answer(f"Ошибка разбора JSON ответа: {e}\nОтвет: {response.text}")
    except Exception as e:
        await message.answer(f"Неизвестная ошибка: {e}")


@router.message(Command("generate_cover_letter"))
async def generate_cover_letter_command(message: types.Message):
    """
    Генерация cover letter на основе описания вакансии.
    Использование: /generate_cover_letter <описание вакансии>
    """
    try:
        job_description = message.text.split(" ", 1)[1]  # Извлекаем описание вакансии

        if not job_description:
            await message.answer(
                "Пожалуйста, укажите описание проекта после команды `/generate_cover_letter`."
            )
            return

        # Генерация cover letter через OpenAI
        from bot import generate_cover_letter  # Импорт функции из основного файла
        cover_letter = await generate_cover_letter(job_description)

        await message.answer(f"Сгенерированное письмо:\n\n{cover_letter}")

    except IndexError:
        await message.answer(
            "Пожалуйста, укажите описание проекта после команды `/generate_cover_letter`."
        )
    except Exception as e:
        await message.answer(f"Неизвестная ошибка: {e}")


@router.message(Command("check_jobs"))
async def check_jobs_command(message: types.Message):
    """
    Команда для ручной проверки новых вакансий.
    """
    await message.answer("Проверяю новые вакансии на Upwork...")
    from bot import check_new_jobs  # Импорт функции из основного файла
    await check_new_jobs()
    await message.answer("Проверка завершена.")


# Глобальная переменная для хранения access token (ВНИМАНИЕ: это небезопасно для production)
ACCESS_TOKEN = None

async def set_bot_commands(bot: Bot):  # Принимаем bot как аргумент
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="help", description="Помощь"),
        types.BotCommand(command="generate_post", description="Сгенерировать пост"),
        types.BotCommand(command="check_jobs", description="Проверить новые вакансии"),
        types.BotCommand(command="generate_cover_letter", description="Сгенерировать сопроводительное письмо"),
    ])