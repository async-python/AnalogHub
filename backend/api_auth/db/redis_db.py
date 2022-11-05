from typing import Optional

from aioredis import Redis

from core.config import AppSettings

settings = AppSettings()

rs: Optional[Redis] = None


# Depend
async def get_redis() -> Redis:
    return rs
