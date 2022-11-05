import abc
from functools import lru_cache

from aioredis import Redis
from fastapi import Depends

from core.config import AppSettings
from db.redis_db import get_redis
from utils.decorators import backoff

conf = AppSettings()


class BaseStorage:
    @abc.abstractmethod
    def save(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        ...

    @abc.abstractmethod
    def retrieve(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        ...

    @abc.abstractmethod
    def delete(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        ...


class RedisStorage(BaseStorage):
    def __init__(self, redis_db: Redis):
        self.redis_db = redis_db

    @backoff()
    async def save(self, key: str, value: str, expire: int) -> None:
        await self.redis_db.set(name=key, value=value, ex=expire)

    @backoff()
    async def retrieve(self, key: str) -> str:
        return await self.redis_db.get(key)

    @backoff()
    async def delete(self, key: str) -> None:
        await self.redis_db.delete(key)


class RedisService:

    def __init__(self, redis_db: Redis):
        self.storage = RedisStorage(redis_db)
        self.exp_access_token_sec = conf.access_token_expire_minutes * 60
        self.exp_refresh_token_sec = conf.refresh_token_expire_days * 86400

    async def save_access_token(self, username: str, token: str) -> None:
        key = username + 'access_token'
        await self.storage.save(key, token, self.exp_access_token_sec)

    async def save_refresh_token(self, username: str, token: str) -> None:
        key = username + 'refresh_token'
        await self.storage.save(key, token, self.exp_refresh_token_sec)

    async def get_access_token(self, username: str) -> str:
        key = username + 'access_token'
        return await self.storage.retrieve(key)

    async def get_refresh_token(self, username: str) -> str:
        key = username + 'refresh_token'
        return await self.storage.retrieve(key)

    async def delete_access_token(self, username: str) -> None:
        key = username + 'access_token'
        await self.storage.delete(key)

    async def delete_refresh_token(self, username: str) -> None:
        key = username + 'refresh_token'
        await self.storage.delete(key)


# Depend
@lru_cache()
def get_redis_service(
        redis_base: Redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis_base)
