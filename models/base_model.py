import uuid
from uuid import UUID

import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonBase(BaseModel):
    id: UUID = Field(
        default_factory=lambda: str(uuid.uuid4()))

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
