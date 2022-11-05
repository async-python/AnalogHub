from typing import Optional

import databases

from core.config import AppSettings

settings = AppSettings()

ps: Optional[databases.Database] = None


# Depend
async def get_postgres() -> databases.Database:
    return ps
