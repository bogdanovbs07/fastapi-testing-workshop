import pytest
import allure
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


@pytest.fixture
def client():
    """Создание синхронного тестового клиента"""
    with allure.step("Создание тестового клиента"):
        return TestClient(app)


@pytest.fixture
async def async_client():
    """Создание асинхронного тестового клиента"""
    with allure.step("Создание асинхронного тестового клиента"):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac


@pytest.fixture
def test_data():
    """Тестовые данные"""
    return {
        "user": {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User"
        },
        "item": {
            "title": "Test Item",
            "description": "Test Description",
            "price": 100.0,
            "tax": 10.0
        }
    }
