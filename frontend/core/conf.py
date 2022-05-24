import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
ENV_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
load_dotenv(ENV_DIR / '.env')


class FlaskConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('POSTGRES_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class UrlConf(BaseSettings):
    fastapi_host: str = 'localhost'
    fastapi_port: str = 8000
    api_version: str = 'v1'

    class Config:
        env_file = ENV_DIR / '.env'

    @property
    def service_url(self):
        return (f'http://{self.fastapi_host}:{self.fastapi_port}/api/'
                f'{self.api_version}/analog/')

    @property
    def search_analog_url(self):
        return self.service_url + 'search_analog'

    @property
    def search_product_url(self):
        return self.service_url + 'search_product'

    @property
    def upload_analogs_url(self):
        return self.service_url + 'upload_analogs'

    @property
    def upload_makers_url(self):
        return self.service_url + 'upload_makers'

    @property
    def search_list_analogs_url(self):
        return self.service_url + 'search_list_analogs'
