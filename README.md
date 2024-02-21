1. ТЗ: https://mnovikov.notion.site/python-d67978e8461c4b009950fcfa83e4f390
2. Перейти в папку с проектом;
3. создать и запустить виртуальное окружение;
4. установить зависимости requirements.txt;
5. Запусить приложение: uvicorn app:app
6. Установить и запустить Celery: celery -A mq worker
7. Запустить Celery beat: celery -A mq beat
7. Прогнать тесты: pytest tests.py
8. Прогнать под нагрузкой: locust --host=http://localhost:8000
9. Потыкать апишку: http://localhost:8000/docs
