# https://github.com/tiangolo/sqlmodel/issues/140#issuecomment-950569807
import uuid as uuid_
from datetime import datetime

import orjson
import sqlalchemy
from pydantic import EmailStr
from sqlalchemy import Column, func
from sqlmodel import Field, SQLModel

from core.config import AppSettings

settings = AppSettings()


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class SQLBaseModel(SQLModel):
    # id generate by db
    id: uuid_.UUID = Field(
        default=sqlalchemy.text('uuid_generate_v4()'),
        primary_key=True,
        index=True,
        nullable=False,
    )

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UserSQL(SQLBaseModel, table=True):
    __tablename__ = settings.postgres_auth_table

    username: str = Field(..., max_length=20, nullable=False)
    email: EmailStr = Field(..., nullable=False, unique=True,
                            index=True)
    full_name: str = Field(..., max_length=100, nullable=False)
    disabled: bool = Field(False, nullable=False)
    is_active: bool = Field(False, nullable=False)
    role: uuid_.UUID = Field(None, foreign_key='roles.id')
    password: str = Field(..., max_length=100, nullable=False)
    salt: str = Field(..., max_length=100, nullable=False)
    # created_at and updated_at generate by db
    created_at: datetime = Field(
        sa_column=Column('created_at', sqlalchemy.DateTime(timezone=True),
                         default=func.now(), nullable=False))
    updated_at: datetime = Field(
        sa_column=Column('updated_at', sqlalchemy.DateTime(timezone=True),
                         default=func.now(),
                         onupdate=func.now, nullable=False))


class RoleSQL(SQLBaseModel, table=True):
    __tablename__ = 'roles'

    name: str = Field(..., max_length=30, unique=True)
    permissions: list[str] = Field(...)
