"""
Тесты для эндпоинтов пользователей.
"""

import pytest
from uuid import uuid4
import logging

from tests.test_models_schemas import UserOutSchema, UsersOutSchema, ErrorResponseSchema

logger = logging.getLogger(__name__)


class TestUsersPositive:
    """Позитивные тесты для пользователей."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_create_user_success(self, client, cleanup_tables, unique_username):
        """Тест успешного создания пользователя."""
        payload = {
            "username": unique_username,
            "is_active": True
        }
        
        response = client.post("/users/", json=payload)
        
        assert response.status_code == 200
        user_data = response.json()
        
        validated = UserOutSchema(**user_data)
        assert validated.username == unique_username
        assert validated.is_active is True
        logger.info(f"Пользователь успешно создан: {user_data['id']}")
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_get_users_list(self, client, cleanup_tables, test_user):
        """Тест получения списка пользователей."""
        response = client.get("/users/")
        
        assert response.status_code == 200
        data = response.json()
        
        validated = UsersOutSchema(**data)
        assert validated.count >= 1
        assert len(validated.data) >= 1
        logger.info(f"Получен список из {validated.count} пользователей")
    
    @pytest.mark.positive
    def test_get_user_by_id(self, client, cleanup_tables, test_user):
        """Тест получения пользователя по ID."""
        response = client.get(f"/users/{test_user.id}")
        
        assert response.status_code == 200
        user_data = response.json()
        
        validated = UserOutSchema(**user_data)
        assert validated.id == test_user.id
        assert validated.username == test_user.username
        logger.info(f"Пользователь получен по ID: {test_user.id}")
    
    @pytest.mark.positive
    @pytest.mark.parametrize("update_data,expected_field,expected_value", [
        ({"username": "updated_user"}, "username", "updated_user"),
        ({"is_active": False}, "is_active", False),
        ({"username": "new_name", "is_active": False}, "username", "new_name"),
    ])
    def test_update_user_success(self, client, cleanup_tables, test_user, update_data, expected_field, expected_value):
        """Тест успешного обновления пользователя с параметризацией."""
        response = client.patch(f"/users/{test_user.id}", json=update_data)
        
        assert response.status_code == 200
        user_data = response.json()
        
        validated = UserOutSchema(**user_data)
        assert getattr(validated, expected_field) == expected_value
        logger.info(f"Пользователь обновлен: {expected_field}={expected_value}")
    
    @pytest.mark.positive
    def test_delete_user_success(self, client, cleanup_tables, test_user):
        """Тест успешного удаления пользователя."""
        response = client.delete(f"/users/{test_user.id}")
        
        assert response.status_code == 200
        assert response.json() == {"status": "deleted"}
        
        get_response = client.get(f"/users/{test_user.id}")
        assert get_response.status_code == 404
        logger.info(f"Пользователь {test_user.id} успешно удален")
    
    @pytest.mark.positive
    def test_happy_path_full_user_flow(self, client, cleanup_tables, unique_username):
        """Тест полного happy path сценария для пользователя."""
        create_payload = {"username": unique_username, "is_active": True}
        create_response = client.post("/users/", json=create_payload)
        assert create_response.status_code == 200
        user_id = create_response.json()["id"]
        logger.info(f"1. Создан пользователь: {user_id}")
        
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        logger.info(f"2. Получен пользователь: {user_id}")
        
        update_payload = {"username": f"{unique_username}_updated"}
        update_response = client.patch(f"/users/{user_id}", json=update_payload)
        assert update_response.status_code == 200
        logger.info(f"3. Обновлен пользователь: {user_id}")
        
        list_response = client.get("/users/")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert any(u["id"] == user_id for u in list_data["data"])
        logger.info(f"4. Пользователь найден в списке")
        
        delete_response = client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 200
        logger.info(f"5. Удален пользователь: {user_id}")
        
        get_deleted_response = client.get(f"/users/{user_id}")
        assert get_deleted_response.status_code == 404
        logger.info("6. Подтверждено удаление пользователя")


class TestUsersNegative:
    """Негативные тесты для пользователей."""
    
    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.parametrize("payload,expected_status,expected_detail", [
        ({}, 422, None),
        ({"is_active": True}, 422, None),
        ({"username": "", "is_active": True}, 422, None),
        ({"username": "a" * 65, "is_active": True}, 422, None),
        ({"username": "a", "is_active": True}, 200, None),
    ])
    def test_create_user_validation(self, client, cleanup_tables, payload, expected_status, expected_detail):
        """Тест валидации при создании пользователя (граничные значения и классы эквивалентности)."""
        response = client.post("/users/", json=payload)
        
        assert response.status_code == expected_status
        
        if expected_status == 422:
            error_data = response.json()
            validated = ErrorResponseSchema(**error_data)
            assert "detail" in error_data
            logger.info(f"Ожидаемая ошибка валидации: {error_data['detail']}")
    
    @pytest.mark.negative
    @pytest.mark.equivalence
    def test_create_duplicate_user(self, client, cleanup_tables, test_user):
        """Тест создания пользователя с дублирующимся username."""
        payload = {
            "username": test_user.username,
            "is_active": True
        }
        
        response = client.post("/users/", json=payload)
        
        assert response.status_code == 409
        error_data = response.json()
        validated = ErrorResponseSchema(**error_data)
        assert "already exists" in error_data["detail"].lower()
        logger.info(f"Ошибка дублирования username: {error_data['detail']}")
    
    @pytest.mark.negative
    @pytest.mark.equivalence
    def test_get_nonexistent_user(self, client, cleanup_tables):
        """Тест получения несуществующего пользователя."""
        fake_id = str(uuid4())
        
        response = client.get(f"/users/{fake_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        validated = ErrorResponseSchema(**error_data)
        assert error_data["detail"] == "User not found"
        logger.info(f"Ошибка получения несуществующего пользователя: {error_data['detail']}")
    
    @pytest.mark.negative
    def test_delete_nonexistent_user(self, client, cleanup_tables):
        """Тест удаления несуществующего пользователя."""
        fake_id = str(uuid4())
        
        response = client.delete(f"/users/{fake_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert error_data["detail"] == "User not found"
        logger.info("Ошибка удаления несуществующего пользователя")
    
    @pytest.mark.negative
    def test_invalid_method(self, client):
        """Тест вызова несуществующего HTTP метода."""
        response = client.put("/users/", json={})
        
        assert response.status_code == 405
        error_data = response.json()
        assert "detail" in error_data
        logger.info(f"Ошибка вызова несуществующего метода: {error_data['detail']}")
