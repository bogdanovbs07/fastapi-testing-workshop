"""
Тесты для утилит.
"""

import pytest
import logging

logger = logging.getLogger(__name__)


class TestUtils:
    """Тесты для утилит."""
    
    @pytest.mark.smoke
    @pytest.mark.positive
    def test_check_db_success(self, client):
        """Тест успешной проверки соединения с БД."""
        response = client.get("/utils/check-db")
        
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}
        logger.info("Соединение с БД успешно проверено")
