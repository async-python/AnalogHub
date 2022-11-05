from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Optional
from uuid import UUID

import databases
from databases.backends.postgres import Record
from fastapi import Depends
from sqlalchemy import insert, select, update

from core.config import AppSettings
from db.postgres_db import get_postgres
from db.ps_schemas.sheme import UserSQL
from models.auth_models.users_models import UserDB, UserLoad
from utils.decorators import backoff

settings = AppSettings()


class AbstractSqlService(ABC):

    @abstractmethod
    async def get_user_by_email(self, email: str):
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[UserDB]:
        ...

    @abstractmethod
    async def check_user_exists(self, email: str) -> bool:
        ...

    @abstractmethod
    async def create_user(self, user: UserLoad):
        ...


class SqlService(AbstractSqlService, ABC):

    def __init__(self, database: databases.Database) -> None:
        self.database: databases = database
        self.user = UserSQL

    @backoff()
    async def check_user_exists(self, email: str) -> bool:
        query = select(self.user.id).where(
            self.user.email == email)
        result: Record = await self.database.fetch_one(query)
        if not result:
            return False
        return True

    @backoff()
    async def get_user_by_email(self, email: str) -> Optional[UserDB]:
        query = select(self.user).where(
            self.user.email == email)
        result: Record = await self.database.fetch_one(query)
        if not result:
            return None
        return UserDB(**result)

    @backoff()
    async def get_user_by_id(self, user_id: str) -> Optional[UserDB]:
        query = select(self.user).where(
            self.user.id == user_id)
        result: Record = await self.database.fetch_one(query)
        if not result:
            return None
        return UserDB(**result)

    @backoff()
    async def create_user(self, user: UserLoad):
        query = insert(self.user).values(**user.dict())
        await self.database.execute(query)


@lru_cache()
def get_sql_service(
        sql_base: databases.Database = Depends(get_postgres)) -> SqlService:
    return SqlService(sql_base)
