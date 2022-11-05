from typing import Optional
from uuid import UUID

from pydantic import Field

from models.base_model import OrjsonBase
from utils.transliterate import delete_symbols


class ToolIn(OrjsonBase):
    """Модель инструмента для пользователя."""

    article: Optional[str] = Field(None, max_length=50)
    title: str
    maker: str = Field(max_length=50)
    description: Optional[str]
    price: float
    currency: str = Field(max_length=5)


class ToolInFull(ToolIn):
    """Модель инструмента для загрузки в postgres."""

    def __init__(self, *args, **kwargs):
        # base_title - поле без лишних символов
        # которое будет использоваться для поиска.
        kwargs['base_title'] = delete_symbols(kwargs['title'])
        super().__init__(*args, **kwargs)  # noqa

    base_title: Optional[str] = None


class ListToolIn(OrjsonBase):
    """Модель загрузки данных инструмента пакетом для пользователя."""
    tools: list[ToolIn] = Field(..., min_items=1, max_items=20000)


class ListToolInDel(OrjsonBase):
    """Модель загрузки данных инструмента пакетом для пользователя."""
    ids: list[UUID] = Field(..., min_items=1, max_items=20000)


class ToolFull(OrjsonBase):
    """Модель используется для получения модели из postgres.
    Необходимы права админа или менеджера, чтобы видеть цены."""

    id: UUID
    article: Optional[str]
    title: str
    maker: str
    description: Optional[str]
    price: float
    currency: str


class ToolSimple(OrjsonBase):
    """Модель используется для получения модели из postgres.
    Юзер с обычными правами не видит цены."""

    id: UUID
    article: Optional[str]
    title: str
    maker: str
    description: Optional[str]


class ToolCreated(OrjsonBase):
    """Используется для успешного ответа при создании
    записи инструмента в postgres."""

    status: str = 'created'


class ToolUpdated(OrjsonBase):
    """Используется для успешного ответа при обновлении
    записи инструмента в postgres."""

    status: str = 'updated'


class ToolDeleted(OrjsonBase):
    """Используется для успешного ответа при удалении
    записи инструмента в postgres."""

    status: str = 'deleted'
