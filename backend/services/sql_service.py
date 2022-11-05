from abc import ABC, abstractmethod
from functools import lru_cache
from uuid import UUID

import databases
import sqlalchemy
from asyncpg import Record, UniqueViolationError
from fastapi import Depends, HTTPException
from sqlalchemy import bindparam

from core.config import AppSettings
from db.postgres_db import get_postgres
from db.ps_schemas.sheme import get_sql_scheme
from models.error_model import Message404
from models.ps_models.tool_models import (ToolCreated, ToolDeleted, ToolIn,
                                          ToolInFull, ToolUpdated)
from utils.error_msg import get_unique_fail_msg

settings = AppSettings()


class AbstractSqlService(ABC):

    @abstractmethod
    async def create_tool(self, tool: ToolIn):
        ...

    @abstractmethod
    async def create_tool_bulk(self, tools: list[ToolIn]):
        ...

    @abstractmethod
    async def get_tools(self, page_num: str, page_size: int):
        ...

    @abstractmethod
    async def get_tool(self, title: str, maker: str):
        ...

    @abstractmethod
    async def update_tool(self, tool: ToolIn):
        ...

    @abstractmethod
    async def update_tool_bulk(self, tools: list[ToolIn]):
        ...

    @abstractmethod
    async def delete_tool(self, uuid: UUID):
        ...

    @abstractmethod
    async def delete_tool_bulk(self, uuid: list[UUID]):
        ...


class SqlService(AbstractSqlService, ABC):

    def __init__(self, database: databases.Database) -> None:
        metadata = sqlalchemy.MetaData()
        self.database: databases = database
        self.table_tools = get_sql_scheme(metadata)
        engine = sqlalchemy.create_engine(settings.postgres_url)
        metadata.create_all(engine)

    async def create_tool(self, tool: ToolIn) -> ToolCreated:
        full_tool = ToolInFull(**tool.dict())
        try:
            query_create = self.table_tools.insert().values(**full_tool.dict())
            await self.database.execute(query_create)
            return ToolCreated()
        except UniqueViolationError as error:
            msg = get_unique_fail_msg(error)
            raise HTTPException(status_code=422, detail=msg)

    async def create_tool_bulk(self, tools: list[ToolIn]) -> ToolCreated:
        try:
            data = self.table_tools.insert().values(
                [ToolInFull(**x.dict()).dict() for x in tools])
            await self.database.execute(data)
            return ToolCreated()
        except UniqueViolationError as error:
            msg = get_unique_fail_msg(error)
            raise HTTPException(status_code=422, detail=msg)

    async def get_tools(self, page_num: str, page_size: int) -> list[Record]:
        offset_val = page_num * page_size
        query = self.table_tools.select().offset(offset_val).limit(page_size)
        return await self.database.fetch_all(query)

    async def get_tool(self, title: str, maker: str) -> Record:
        query = self.table_tools.select().where(
            self.table_tools.c.title == title,
            self.table_tools.c.maker == maker)
        result = await self.database.fetch_one(query)
        if not result:
            raise HTTPException(status_code=404, detail=Message404().detail)
        return result

    async def update_tool(self, tool: ToolIn):
        tool_db: Record = await self.get_tool(tool.title, tool.maker)
        tool_id: UUID = dict(**tool_db).get('id')
        tool_upd = ToolInFull(**tool.dict())
        query = self.table_tools.update(
            self.table_tools.c.id == tool_id, values=tool_upd.dict())
        await self.database.execute(query)
        return ToolUpdated()

    async def update_tool_bulk(self, tools: list[ToolIn]):
        tools_load = []
        for tool in tools:
            tool_db: Record = await self.get_tool(tool.title, tool.maker)
            tool_id: UUID = dict(**tool_db).get('id')
            tool_upd = ToolInFull(**tool.dict())
            tools_load.append({'id': tool_id} | tool_upd.dict())
        query = self.table_tools.update(
            self.table_tools.c.id == bindparam('id')).values(
            {
                'article': bindparam('article'),
                'title': bindparam('title'),
                'base_title': bindparam('base_title'),
                'maker': bindparam('maker'),
                'description': bindparam('description'),
                'price': bindparam('price'),
                'currency': bindparam('currency')
            })
        try:
            await self.database.execute_many(
                query=str(query), values=tools_load)
            return ToolUpdated()
        except UniqueViolationError as error:
            msg = get_unique_fail_msg(error)
            raise HTTPException(status_code=422, detail=msg)

    async def delete_tool(self, uuid: UUID):
        del_query = self.table_tools.delete(self.table_tools.c.id == uuid)
        await self.database.execute(del_query)
        return ToolDeleted()

    async def delete_tool_bulk(self, tool_ids: list[UUID]):
        del_query = self.table_tools.delete(
            self.table_tools.c.id.in_(tool_ids))
        await self.database.execute(del_query)
        return ToolDeleted()


@lru_cache()
def get_sql_service(
        sql_base: databases.Database = Depends(get_postgres)) -> SqlService:
    return SqlService(sql_base)
