from abc import abstractmethod
from datetime import datetime
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from fastapi import Depends

from core.config import AppSettings
from db.redis_db import get_redis
from utils.decorators import backoff

conf = AppSettings()


class BaseStorage:
    @abstractmethod
    def save(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        ...

    @abstractmethod
    def retrieve(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        ...

    @abstractmethod
    async def exists(self, key: str):
        """Проверить наличие ключа в БД"""
        ...

    @abstractmethod
    def delete(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        ...


class RedisStorage(BaseStorage):
    def __init__(self, redis_db: Redis):
        self.redis_db = redis_db

    @backoff()
    async def save(self, key: str, value: Optional[str], expire: int) -> None:
        await self.redis_db.set(name=key, value=value, ex=expire)

    @backoff()
    async def retrieve(self, key: str) -> str:
        return await self.redis_db.get(key)

    @backoff()
    async def exists(self, key: str):
        return await self.redis_db.exists(key)

    @backoff()
    async def delete(self, key: str) -> None:
        await self.redis_db.delete(key)


class RedisService:

    def __init__(self, redis_db: Redis):
        self.storage = RedisStorage(redis_db)
        # days -> seconds
        self.exp_refresh_token_sec = conf.refresh_token_expire_days * 86400

    async def save_invalid_access_token(
            self, token: str, expire: datetime) -> None:
        delta = expire.replace(
            tzinfo=None) - datetime.utcnow().replace(tzinfo=None)
        await self.storage.save(token, '', delta.seconds)

    async def check_access_token_invalid(self, token: str) -> str:
        return await self.storage.exists(token)

    async def save_refresh_token(self, user_id: str, token: str) -> None:
        key = user_id + '_refresh_token'
        await self.storage.save(key, token, self.exp_refresh_token_sec)

    async def get_refresh_token(self, user_id: str) -> str:
        key = user_id + '_refresh_token'
        return await self.storage.retrieve(key)

    async def delete_refresh_token(self, user_id: str) -> None:
        key = user_id + '_refresh_token'
        await self.storage.delete(key)


# Depend
@lru_cache()
def get_redis_service(
        redis_base: Redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis_base)
