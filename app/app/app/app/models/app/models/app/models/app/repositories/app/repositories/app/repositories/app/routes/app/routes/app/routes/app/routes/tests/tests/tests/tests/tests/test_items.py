"""
Тесты для эндпоинтов элементов.
"""

import pytest
from uuid import uuid4
import logging

from tests.test_models_schemas import ItemOutSchema, ItemsOutSchema, ErrorResponseSchema

logger = logging.getLogger(__name__)


class TestItemsPositive:
    """Позитивные тесты для элементов."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_create_item_success(self, client, cleanup_tables, test_user, unique_item_title):
        """Тест успешного создания элемента."""
        payload = {
            "title": unique_item_title,
            "description": "Test description for item"
        }
        
        response = client.post(f"/users/{test_user.id}/items", json=payload)
        
        assert response.status_code == 200
        item_data = response.json()
        
        # Валидация JSON-схемы
        validated = ItemOutSchema(**item_data)
        assert validated.title == unique_item_title
        assert validated.user_id == test_user.id
        logger.info(f"Элемент успешно создан: {item_data['id']}")
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_items_list(self, client, cleanup_tables, test_item):
        """Тест получения списка элементов."""
        response = client.get("/items/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Валидация JSON-схемы
        validated = ItemsOutSchema(**data)
        assert validated.count >= 1
        assert len(validated.data) >= 1
        logger.info(f"Получен список из {validated.count} элементов")
    
    @pytest.mark.positive
    def test_get_item_by_id(self, client, cleanup_tables, test_item):
        """Тест получения элемента по ID."""
        response = client.get(f"/items/{test_item.id}")
        
        assert response.status_code == 200
        item_data = response.json()
        
        validated = ItemOutSchema(**item_data)
        assert validated.id == test_item.id
        assert validated.title == test_item.title
        logger.info(f"Элемент получен по ID: {test_item.id}")
    
    @pytest.mark.positive
    def test_get_user_items(self, client, cleanup_tables, test_user, test_item):
        """Тест получения элементов конкретного пользователя."""
        response = client.get(f"/users/{test_user.id}/items")
        
        assert response.status_code == 200
        data = response.json()
        
        validated = ItemsOutSchema(**data)
        assert validated.count >= 1
        assert all(item["user_id"] == str(test_user.id) for item in validated.data)
        logger.info(f"Получены элементы пользователя: {test_user.id}")
    
    @pytest.mark.positive
    @pytest.mark.parametrize("update_data,expected_field,expected_value", [
        ({"title": "Updated Title"}, "title", "Updated Title"),
        ({"description": "Updated Description"}, "description", "Updated Description"),
        ({"title": "New Title", "description": "New Description"}, "title", "New Title"),
    ])
    def test_update_item_success(self, client, cleanup_tables, test_item, update_data, expected_field, expected_value):
        """Тест успешного обновления элемента с параметризацией."""
        response = client.patch(f"/items/{test_item.id}", json=update_data)
        
        assert response.status_code == 200
        item_data = response.json()
        
        validated = ItemOutSchema(**item_data)
        assert getattr(validated, expected_field) == expected_value
        logger.info(f"Элемент обновлен: {expected_field}={expected_value}")
    
    @pytest.mark.positive
    def test_delete_item_success(self, client, cleanup_tables, test_item):
        """Тест успешного удаления элемента."""
        response = client.delete(f"/items/{test_item.id}")
        
        assert response.status_code == 200
        assert response.json() == {"status": "deleted"}
        
        # Проверяем, что элемент действительно удален
        get_response = client.get(f"/items/{test_item.id}")
        assert get_response.status_code == 404
        logger.info(f"Элемент {test_item.id} успешно удален")


class TestItemsNegative:
    """Негативные тесты для элементов."""
    
    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize("payload,expected_status", [
        ({}, 422),
        ({"description": "No title"}, 422),
        ({"title": "", "description": "test"}, 422),
        ({"title": "a" * 129, "description": "test"}, 422),
        ({"title": "a", "description": "test"}, 200),
        ({"title": "a" * 128, "description": "test"}, 200),
    ])
    def test_create_item_validation(self, client, cleanup_tables, test_user, payload, expected_status):
        """Тест валидации при создании элемента (граничные значения и классы эквивалентности)."""
        response = client.post(f"/users/{test_user.id}/items", json=payload)
        
        assert response.status_code == expected_status
        
        if expected_status == 422:
            error_data = response.json()
            validated = ErrorResponseSchema(**error_data)
            assert "detail" in error_data
            logger.info(f"Ожидаемая ошибка валидации: {error_data['detail']}")
        else:
            logger.info("Элемент успешно создан")
    
    @pytest.mark.negative
    @pytest.mark.equivalence
    def test_create_item_for_nonexistent_user(self, client, cleanup_tables):
        """Тест создания элемента для несуществующего пользователя."""
        fake_user_id = str(uuid4())
        payload = {
            "title": "Test Item",
            "description": "Test"
        }
        
        response = client.post(f"/users/{fake_user_id}/items", json=payload)
        
        assert response.status_code == 404
        error_data = response.json()
        validated = ErrorResponseSchema(**error_data)
        assert error_data["detail"] == "User not found"
        logger.info("Ошибка создания элемента для несуществующего пользователя")
    
    @pytest.mark.negative
    @pytest.mark.equivalence
    def test_get_nonexistent_item(self, client, cleanup_tables):
        """Тест получения несуществующего элемента."""
        fake_id = str(uuid4())
        
        response = client.get(f"/items/{fake_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        validated = ErrorResponseSchema(**error_data)
        assert error_data["detail"] == "Item not found"
        logger.info("Ошибка получения несуществующего элемента")
    
    @pytest.mark.negative
    def test_delete_nonexistent_item(self, client, cleanup_tables):
        """Тест удаления несуществующего элемента."""
        fake_id = str(uuid4())
        
        response = client.delete(f"/items/{fake_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert error_data["detail"] == "Item not found"
        logger.info("Ошибка удаления несуществующего элемента")
