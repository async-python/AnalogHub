from logging import config as logging_config
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings

from core.logger import LOGGING

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

load_dotenv()

logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    project_name: str = 'AnalogHub Auth Service'

    postgres_auth_table: str = 'auth'
    postgres_db: str = 'auth'
    postgres_user: str = 'postgres'
    postgres_password: str = 'Adgjmptw1'
    postgres_host: str = 'localhost'
    postgres_port: int = 5432

    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str
    redis_base: int = 1

    service_host: str = 'localhost'
    service_port: str = 8000
    api_version: str = 'v1'

    secret_key: str = 'the_very_secret_secret'
    secret_key_refresh: str = 'the_very_secret_secret2'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 90
    refresh_token_expire_days: int = 5

    class Config:
        env_file = '.env'

    @property
    def postgres_url(self):
        ps_url = 'postgresql+asyncpg://'
        ps_url += f'{self.postgres_user}:{self.postgres_password}@'
        ps_url += f'{self.postgres_host}:{self.postgres_port}/'
        ps_url += f'{self.postgres_db}'
        return ps_url
