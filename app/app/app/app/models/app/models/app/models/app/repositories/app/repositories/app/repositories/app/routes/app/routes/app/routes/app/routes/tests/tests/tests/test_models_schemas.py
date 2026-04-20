"""
Модели Pydantic для валидации JSON-схем в тестах.
Важно: модели определены отдельно от основного кода для фиксации контракта API.
"""

from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserOutSchema(BaseModel):
    """Схема ответа API для пользователя."""
    model_config = ConfigDict(extra="forbid")
    
    id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    username: str = Field(..., min_length=1, max_length=64, description="Имя пользователя")
    is_active: bool = Field(..., description="Статус активности")


class UsersOutSchema(BaseModel):
    """Схема ответа API для списка пользователей."""
    model_config = ConfigDict(extra="forbid")
    
    data: list[UserOutSchema] = Field(..., description="Список пользователей")
    count: int = Field(..., ge=0, description="Общее количество пользователей")


class ItemOutSchema(BaseModel):
    """Схема ответа API для элемента."""
    model_config = ConfigDict(extra="forbid")
    
    id: UUID = Field(..., description="Уникальный идентификатор элемента")
    title: str = Field(..., min_length=1, max_length=128, description="Название элемента")
    description: Optional[str] = Field(None, max_length=500, description="Описание элемента")
    user_id: UUID = Field(..., description="ID владельца")


class ItemsOutSchema(BaseModel):
    """Схема ответа API для списка элементов."""
    model_config = ConfigDict(extra="forbid")
    
    data: list[ItemOutSchema] = Field(..., description="Список элементов")
    count: int = Field(..., ge=0, description="Общее количество элементов")


class ErrorResponseSchema(BaseModel):
    """Схема ответа API для ошибок."""
    model_config = ConfigDict(extra="forbid")
    
    detail: str = Field(..., description="Описание ошибки")
