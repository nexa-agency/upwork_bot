import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_cover_letter(job_description, template=""):
    """Генерирует Cover Letter с использованием OpenAI API."""
    prompt = f"""
    Напиши Cover Letter для вакансии: {job_description}
    Используй следующий шаблон: {template}
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Или другая подходящая модель
            prompt=prompt,
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Ошибка при запросе к OpenAI API: {e}")
        return None

if __name__ == '__main__':
    job_description = "Нужен Telegram-бот для автоматической подачи заявок на вакансии с Upwork."
    cover_letter = generate_cover_letter(job_description)
    print(cover_letter)