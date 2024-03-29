from logging import config as logging_config
from pathlib import Path

from core.logger import LOGGING
from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

load_dotenv()

logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    project_name = 'AnalogHub'

    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str

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
