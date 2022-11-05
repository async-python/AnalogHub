import sqlalchemy
from sqlalchemy import Column, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from core.config import AppSettings

settings = AppSettings()


def get_sql_scheme(metadata: sqlalchemy.MetaData) -> sqlalchemy.Table:
    table_tools = sqlalchemy.Table(
        settings.sql_tool_table_name,
        metadata,
        sqlalchemy.Column('id', UUID,
                          primary_key=True,
                          server_default=sqlalchemy.text(
                              "uuid_generate_v4()"),
                          index=True),
        Column('article', sqlalchemy.String(50), nullable=True),
        Column('title', sqlalchemy.String, nullable=False),
        Column('base_title', sqlalchemy.String, nullable=False,
               index=True),
        Column('maker', sqlalchemy.String(50), nullable=False),
        Column('description', sqlalchemy.String, nullable=True),
        Column('price', sqlalchemy.Float),
        Column('currency', sqlalchemy.String(5)),
        Column('created_at', sqlalchemy.DateTime(timezone=True),
               default=func.now()),
        Column('updated_at',
               sqlalchemy.DateTime(timezone=True), default=func.now(),
               onupdate=func.now()),
        UniqueConstraint('base_title', 'maker',
                         name='unique_base_title_maker')
    )
    return table_tools
