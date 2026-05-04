import allure
import pytest
import json


@allure.feature("API Testing")
@allure.story("Health Check")
class TestHealthCheck:
    
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Проверка работоспособности API")
    @allure.description("Тест проверяет, что API отвечает на корневой эндпоинт")
    def test_root_endpoint(self, client):
        with allure.step("Отправка GET запроса на корневой эндпоинт"):
            response = client.get("/")
            
        with allure.step("Проверка статус кода"):
            assert response.status_code == 200
            
        with allure.step("Проверка тела ответа"):
            data = response.json()
            assert "message" in data
            
        with allure.step("Прикрепление ответа к отчету"):
            allure.attach(
                json.dumps(data, indent=2),
                name="Response Body",
                attachment_type=allure.attachment_type.JSON
            )
    
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Проверка health-check эндпоинта")
    @allure.description("Тест проверяет эндпоинт проверки здоровья сервиса")
    def test_health_check(self, client):
        with allure.step("Отправка GET запроса на /health"):
            response = client.get("/health")
            
        with allure.step("Проверка статус кода 200"):
            assert response.status_code == 200
            
        with allure.step("Проверка статуса health check"):
            data = response.json()
            assert data["status"] == "healthy"
            
        allure.attach(
            json.dumps(data, indent=2),
            name="Health Check Response",
            attachment_type=allure.attachment_type.JSON
        )


@allure.feature("API Testing")
@allure.story("Users Management")
class TestUsers:
    
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Создание нового пользователя")
    @allure.description("Тест проверяет создание пользователя через POST запрос")
    @allure.tag("smoke", "regression")
    def test_create_user(self, client, test_data):
        with allure.step("Подготовка данных пользователя"):
            user_data = test_data["user"]
            allure.attach(
                json.dumps(user_data, indent=2),
                name="User Data",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Отправка POST запроса на создание пользователя"):
            response = client.post("/users/", json=user_data)
        
        with allure.step("Проверка статус кода 201"):
            assert response.status_code == 201
            
        with allure.step("Проверка данных созданного пользователя"):
            created_user = response.json()
            assert created_user["username"] == user_data["username"]
            assert created_user["email"] == user_data["email"]
            assert "id" in created_user
            
        allure.attach(
            json.dumps(created_user, indent=2),
            name="Created User Response",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Получение списка пользователей")
    @allure.description("Тест проверяет получение списка всех пользователей")
    def test_get_users(self, client, test_data):
        with allure.step("Создание тестового пользователя"):
            client.post("/users/", json=test_data["user"])
        
        with allure.step("Отправка GET запроса на получение пользователей"):
            response = client.get("/users/")
        
        with allure.step("Проверка статус кода 200"):
            assert response.status_code == 200
            
        with allure.step("Проверка списка пользователей"):
            users = response.json()
            assert isinstance(users, list)
            assert len(users) > 0
            
        allure.attach(
            json.dumps(users, indent=2),
            name="Users List Response",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Получение пользователя по ID")
    @allure.description("Тест проверяет получение пользователя по идентификатору")
    @allure.tag("regression")
    def test_get_user_by_id(self, client, test_data):
        with allure.step("Создание пользователя для теста"):
            create_response = client.post("/users/", json=test_data["user"])
            user_id = create_response.json()["id"]
        
        with allure.step(f"Получение пользователя с ID={user_id}"):
            response = client.get(f"/users/{user_id}")
        
        with allure.step("Проверка статус кода 200"):
            assert response.status_code == 200
            
        with allure.step("Проверка данных пользователя"):
            user = response.json()
            assert user["id"] == user_id
            assert user["username"] == test_data["user"]["username"]
            
        allure.attach(
            json.dumps(user, indent=2),
            name=f"User {user_id} Response",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Получение несуществующего пользователя")
    @allure.description("Тест проверяет обработку запроса несуществующего пользователя")
    def test_get_nonexistent_user(self, client):
        with allure.step("Отправка GET запроса с несуществующим ID"):
            response = client.get("/users/99999")
        
        with allure.step("Проверка статус кода 404"):
            assert response.status_code == 404
            
        allure.attach(
            json.dumps(response.json(), indent=2),
            name="Error Response",
            attachment_type=allure.attachment_type.JSON
        )


@allure.feature("API Testing")
@allure.story("Items Management")
class TestItems:
    
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Создание нового товара")
    @allure.description("Тест проверяет создание товара через POST запрос")
    @allure.tag("smoke")
    def test_create_item(self, client, test_data):
        with allure.step("Подготовка данных товара"):
            item_data = test_data["item"]
            allure.attach(
                json.dumps(item_data, indent=2),
                name="Item Data",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Отправка POST запроса на создание товара"):
            response = client.post("/items/", json=item_data)
        
        with allure.step("Проверка статус кода 201"):
            assert response.status_code == 201
            
        with allure.step("Проверка данных созданного товара"):
            created_item = response.json()
            assert created_item["title"] == item_data["title"]
            assert created_item["price"] == item_data["price"]
            
        allure.attach(
            json.dumps(created_item, indent=2),
            name="Created Item Response",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Создание товара с некорректными данными")
    @allure.description("Тест проверяет валидацию при создании товара")
    def test_create_item_invalid_data(self, client):
        with allure.step("Подготовка некорректных данных"):
            invalid_data = {"title": "", "price": -100}
        
        with allure.step("Отправка POST запроса с некорректными данными"):
            response = client.post("/items/", json=invalid_data)
        
        with allure.step("Проверка статус кода 422"):
            assert response.status_code == 422
            
        allure.attach(
            json.dumps(response.json(), indent=2),
            name="Validation Error Response",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Получение списка товаров")
    @allure.description("Тест проверяет получение списка всех товаров")
    @allure.tag("regression")
    def test_get_items(self, client, test_data):
        with allure.step("Создание тестового товара"):
            client.post("/items/", json=test_data["item"])
        
        with allure.step("Отправка GET запроса на получение товаров"):
            response = client.get("/items/")
        
        with allure.step("Проверка статус кода 200"):
            assert response.status_code == 200
            
        with allure.step("Проверка списка товаров"):
            items = response.json()
            assert isinstance(items, list)
            assert len(items) > 0
            
        allure.attach(
            json.dumps(items, indent=2),
            name="Items List Response",
            attachment_type=allure.attachment_type.JSON
        )


@allure.feature("API Testing")
@allure.story("Async Operations")
class TestAsyncOperations:
    
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Асинхронное создание нескольких пользователей")
    @allure.description("Тест проверяет параллельное создание пользователей")
    @allure.tag("async", "performance")
    @pytest.mark.asyncio
    async def test_async_create_users(self, async_client, test_data):
        users_data = [
            {"username": "user1", "email": "user1@test.com"},
            {"username": "user2", "email": "user2@test.com"},
            {"username": "user3", "email": "user3@test.com"}
        ]
        
        with allure.step("Параллельная отправка POST запросов"):
            responses = []
            for user_data in users_data:
                response = await async_client.post("/users/", json=user_data)
                responses.append(response)
        
        with allure.step("Проверка всех ответов"):
            for i, response in enumerate(responses):
                assert response.status_code == 201
                created_user = response.json()
                assert created_user["username"] == users_data[i]["username"]
                
                allure.attach(
                    json.dumps(created_user, indent=2),
                    name=f"User {i+1} Response",
                    attachment_type=allure.attachment_type.JSON
                )


@allure.feature("API Testing")
@allure.story("Error Handling")
class TestErrorHandling:
    
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Проверка обработки некорректного JSON")
    @allure.description("Тест проверяет обработку невалидного JSON в запросе")
    def test_invalid_json(self, client):
        with allure.step("Отправка POST запроса с некорректным JSON"):
            response = client.post(
                "/users/",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
        
        with allure.step("Проверка статус кода 422"):
            assert response.status_code == 422
            
        allure.attach(
            json.dumps(response.json(), indent=2),
            name="Error Response",
            attachment_type=allure.attachment_type.JSON
        )
    
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Проверка обработки метода не разрешенного для эндпоинта")
    @allure.description("Тест проверяет ответ на некорректный HTTP метод")
    def test_method_not_allowed(self, client):
        with allure.step("Отправка PUT запроса на GET-only эндпоинт"):
            response = client.put("/users/")
        
        with allure.step("Проверка статус кода 405"):
            assert response.status_code == 405
            
        allure.attach(
            json.dumps(response.json(), indent=2),
            name="Method Not Allowed Response",
            attachment_type=allure.attachment_type.JSON
        )
