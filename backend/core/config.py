from logging import config as logging_config
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings

from core.logger import LOGGING

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

load_dotenv()

logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    project_name: str = 'AnalogHub'

    sql_tool_table_name: str = 'tools'
    postgres_db: str = 'tools'
    postgres_user: str = 'postgres'
    postgres_password: str = 'Adgjmptw1'
    postgres_host: str = 'localhost'
    postgres_port: int = 5432

    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str
    redis_base: int = 1

    elastic_host: str = 'localhost'
    elastic_port: int = 9200
    elastic_user: str = 'elastic'
    elastic_scheme: str = 'http'
    es_index_analog = 'analog'
    es_index_product = 'product'

    service_host: str = 'localhost'
    service_port: str = 8000
    api_version: str = 'v1'
    priority_brands = ['PALBIT', 'VARGUS', 'VERGNANO',
                       'DEREK', 'BRICE', 'OMAP']

    file_path = BASE_DIR / 'file_storage'
    secret_key: str = 'the_very_secret_secret'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 10

    class Config:
        env_file = '.env'

    @property
    def redis_url(self):
        return (
            f'redis://:{self.redis_password}'
            f'@{self.redis_host}:{self.redis_port}/0')

    @property
    def elastic_url(self):
        return f'http://{self.elastic_host}:{self.elastic_port}'

    @property
    def postgres_url(self):
        return f'''postgresql://{self.postgres_user}:{self.postgres_password}
        @{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'''
