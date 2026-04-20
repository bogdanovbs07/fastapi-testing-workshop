import asyncio
import logging
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql import text

from app.main import app
from app.database import get_session
from app.models.users import User
from app.models.items import Item

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Добавление пользовательских опций командной строки."""
    parser.addoption(
        "--db-url",
        action="store",
        default="postgresql+asyncpg://postgres:1234@localhost:5432/Test",
        help="URL подключения к тестовой базе данных"
    )
    parser.addoption(
        "--keep-db",
        action="store_true",
        default=False,
        help="Не очищать базу данных после тестов"
    )


@pytest.fixture(scope="session")
def db_url(request) -> str:
    """Фикстура для получения URL базы данных из опций командной строки."""
    return request.config.getoption("--db-url")


@pytest.fixture(scope="session")
def engine(db_url: str):
    """Создание асинхронного движка для тестовой БД."""
    engine = create_async_engine(db_url, echo=True)
    return engine


@pytest.fixture(scope="function")
async def async_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для асинхронной сессии базы данных."""
    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        logger.info(f"Создана тестовая сессия: {id(session)}")
        yield session


@pytest.fixture(scope="function")
def client(async_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Фикстура для тестового клиента FastAPI."""
    
    async def override_get_session():
        yield async_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        logger.info("Создан тестовый клиент")
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def cleanup_tables(async_session: AsyncSession):
    """Фикстура для очистки таблиц перед тестом."""
    tables = ["items", "users"]
    for table in tables:
        await async_session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    await async_session.commit()
    logger.info("Таблицы очищены перед тестом")
    yield
    logger.info("Тест завершен, очистка таблиц")


@pytest.fixture
def unique_username() -> str:
    """Генерация уникального username для тестов."""
    return f"test_user_{uuid4().hex[:8]}"


@pytest.fixture
def unique_item_title() -> str:
    """Генерация уникального title для тестов."""
    return f"Test Item {uuid4().hex[:8]}"


@pytest.fixture
async def test_user(async_session: AsyncSession, unique_username: str) -> User:
    """Создание тестового пользователя."""
    user = User(username=unique_username, is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    logger.info(f"Создан тестовый пользователь: {user.id}")
    return user


@pytest.fixture
async def test_item(async_session: AsyncSession, test_user: User, unique_item_title: str) -> Item:
    """Создание тестового элемента."""
    item = Item(title=unique_item_title, description="Test Description", user=test_user)
    async_session.add(item)
    await async_session.commit()
    await async_session.refresh(item)
    logger.info(f"Создан тестовый элемент: {item.id}")
    return item


def pytest_sessionfinish(session, exitstatus):
    """Хук, вызываемый после завершения всех тестов."""
    logger.info(f"Сессия тестов завершена с exitstatus: {exitstatus}")
    
    keep_db = session.config.getoption("--keep-db")
    
    if exitstatus == 0:
        logger.info("Все тесты прошли успешно!")
        if not keep_db:
            logger.info("База данных будет очищена")
    else:
        logger.warning("Есть упавшие тесты!")
        if not keep_db:
            logger.info("База данных НЕ будет очищена из-за ошибок в тестах")
