# FastAPI Testing Workshop

Проект для обучения тестированию FastAPI приложений с использованием pytest.

## Описание проекта

Простое API для управления пользователями и их элементами (items).

## Технологии

- FastAPI
- SQLModel
- PostgreSQL (asyncpg)
- Pytest
- Pydantic

## Установка

```bash
pip install -r requirements.txt



Запуск
uvicorn app.main:app --reload



Тестирование
# Запуск всех тестов
pytest

# Запуск с отчетом о покрытии
pytest --cov=app --cov-report=html

# Запуск только smoke тестов
pytest -m smoke

# Запуск с указанием своей БД
pytest --db-url="postgresql+asyncpg://user:pass@localhost:5432/test_db"



Структура проекта
project/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── repositories/
│   └── routes/
├── tests/
│   ├── conftest.py
│   ├── test_models_schemas.py
│   ├── test_users.py
│   ├── test_items.py
│   └── test_utils.py
├── requirements.txt
└── pytest.ini


4. Прокрути вниз и нажми зеленую кнопку **"Commit changes..."**

5. В появившемся окне:
   - Оставь сообщение коммита по умолчанию: "Create README.md"
   - Убедись что выбрано "Commit directly to the main branch"
   - Нажми **"Commit changes"**


1. Нажми **"Add file"** → **"Create new file"**

2. Имя файла: `requirements.txt`

3. Содержимое:

fastapi==0.104.1
sqlmodel==0.0.14
sqlalchemy==2.0.23
asyncpg==0.29.0
pydantic==2.5.2
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1
uvicorn==0.24.0

4. Нажми **"Commit changes..."** → **"Commit changes"**


1. Нажми **"Add file"** → **"Create new file"**

2. Имя файла: `pytest.ini`

3. Содержимое:
```ini
[pytest]
minversion = 6.0
addopts = 
    -ra -q
    -v
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --log-cli-level=INFO
    --log-file=logs/pytest.log
testpaths = tests
markers =
    smoke: Критические тесты для быстрой проверки
    regress: Тесты для регрессионного тестирования
    positive: Позитивные тесты (happy path)
    negative: Негативные тесты (валидация ошибок)
    boundary: Тесты граничных значений
    equivalence: Тесты классов эквивалентности
    schema: Тесты валидации JSON-схем
log_level = INFO
log_format = %(asctime)s [%(levelname)s] %(name)s: %(message)s
log_date_format = %Y-%m-%d %H:%M:%S
