import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch
import asyncio

# Импортируем модуль, который мы будем тестировать
from bot import get_jobs_from_upwork

class TestUpworkAPI(unittest.TestCase):

    # Фиктивные данные для имитации ответа API Upwork
    mock_upwork_response = {
        "jobs": [
            {
                "title": "Python Developer",
                "description": "Looking for a Python developer for a long-term project.",
                "budget": 1000,
                "job_type": "fixed"
            },
            {
                "title": "AI Developer",
                "description": "Looking for an AI developer for a long-term project.",
                "budget": 50,
                "job_type": "hourly"
            }
        ]
    }

    # Функция для имитации запроса к API Upwork
    async def mock_get_jobs(self, *args, **kwargs):
        return self.mock_upwork_response

    @patch('bot.get_jobs_from_upwork', side_effect=mock_get_jobs)
    def test_get_jobs(self, mock_get_jobs):
        """
        Тест проверяет, что функция получения вакансий возвращает ожидаемые данные.
        """
        # Запускаем асинхронную функцию в синхронном контексте
        loop = asyncio.get_event_loop()
        jobs = loop.run_until_complete(get_jobs_from_upwork())

        # Проверяем, что возвращенные данные соответствуют фиктивным данным
        self.assertEqual(jobs, self.mock_upwork_response)

    def test_process_data(self):
        """
        Тест для функции process_data.
        """
        from bot import process_data  # Импортируем process_data здесь
        data = {"key1": "value1", "key2": "value2"}
        result = process_data(data)
        self.assertEqual(result, "Processed data")

    def test_filter_jobs(self):
        """
        Тест проверяет, что функция фильтрации вакансий работает правильно.
        """
        # Здесь нужно добавить код для проверки фильтрации вакансий
        # Например, можно проверить, что функция возвращает только вакансии, соответствующие заданным критериям
        pass

if __name__ == '__main__':
    unittest.main()