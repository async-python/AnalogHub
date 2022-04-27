from logging import config as logging_config
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings

from core.logger import LOGGING

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

load_dotenv()

logging_config.dictConfig(LOGGING)


class AppSettings(BaseSettings):
    project_name = 'Analogs'

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

    class Config:
        env_file = '.env'

    @property
    def redis_url(self):
        return (f'redis://'
                f':{self.redis_password}@{self.redis_host}:{self.redis_port}')

    @property
    def elastic_url(self):
        return f'http://{self.elastic_host}:{self.elastic_port}'
