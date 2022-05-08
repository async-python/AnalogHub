import os
import shutil
import uuid
import zipfile
from os import listdir
from os.path import isfile, join
from shutil import rmtree
from typing import Iterable

import arrow
import pandas as pd
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from elasticsearch import Elasticsearch

from core.config import BASE_DIR, AppSettings
from models.input.model_analog import DataAnalogEntry
from services.file_utils import get_columns_locs
from services.mappings import makers_map

settings = AppSettings()

celery_app = Celery(__name__)
celery_app.conf.broker_url = settings.redis_url
celery_app.conf.result_backend = settings.redis_url

celery_app.autodiscover_tasks()

elastic = Elasticsearch(hosts=settings.elastic_url)
celery_log = get_task_logger(__name__)

etl_butch_size = 10000


def get_task_result(task_id):
    return celery_app.AsyncResult(task_id)


def bulk_es_data(data: list, index: str):
    body = []
    for model in data:
        head = {'index': {'_index': index, '_id': model.id}}
        body.append(head)
        body.append(model.dict())
    elastic.bulk(index=index, operations=body)


def load_es_data_partially(data: Iterable, es_index: str):
    counter = 0
    dump = []
    for item in data:
        if counter < etl_butch_size:
            dump.append(item)
            counter += 1
        else:
            bulk_es_data(dump, es_index)
            counter = 0
            dump = []
    if len(dump):
        bulk_es_data(dump, es_index)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=1), delete_old_files.s(), name='clear old files')


@celery_app.task(name='upload_elastic_analogs')
def upload_elastic_analogs(file_path):
    try:
        with open(file_path, 'rb') as f:
            xls = pd.read_excel(f, 0, keep_default_na=False)
            locs = get_columns_locs(xls)
            transform = lambda x: DataAnalogEntry(
                base_name=x[locs.get('base_col_num')],
                base_maker=x[locs.get('base_maker_col_num')],
                analog_name=x[locs.get('analog_col_num')],
                analog_maker=x[locs.get('analog_maker_col_num')])
            list_data_cls = (transform(x) for x in [*xls.values.tolist()])
            load_es_data_partially(list_data_cls, settings.es_index_analog)
        os.remove(file_path)
        return {'state': 'ok'}
    except Exception as error:
        celery_log.info(error)
        os.remove(file_path)
        return {'state': 'fail'}


@celery_app.task(name='upload_elastic_makers')
def upload_elastic_makers(file_path: str, file_name: str):
    file_path_zip = str(
        BASE_DIR.joinpath('file_storage') / str(uuid.uuid4())) + '/'
    path_unpack = file_path_zip + file_name[:-4] + '/'
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(file_path_zip)
        only_files = [file for file in listdir(path_unpack) if
                      isfile(join(path_unpack, file))]
        for file in only_files:
            with open(path_unpack + file, 'rb') as f:
                exel: list = pd.read_excel(  # noqa
                    f, 0, keep_default_na=False).values.tolist()
                maker = None
                all_keys = makers_map.keys()
                for key in all_keys:
                    if file.startswith(key):
                        maker = key
                func = makers_map.get(maker)
                if maker:
                    list_data_product = (func(x) for x in exel)
                    load_es_data_partially(list_data_product,
                                           settings.es_index_product)
        os.remove(file_path)
        rmtree(file_path_zip)
        return {'state': 'ok'}
    except Exception as error:
        celery_log.info(error)
        os.remove(file_path)
        rmtree(file_path_zip)
        return {'state': 'fail'}


@celery_app.task
def delete_old_files():
    path = settings.file_path
    celery_log.info('Period Task Deleting Old Files started')
    critical_time = arrow.now().shift(hours=-1)
    for item in path.glob('*'):
        item_path = path / item
        item_time = arrow.get(item.stat().st_mtime)
        if item.is_file():
            if item_time < critical_time:
                celery_log.info(f'deleting file: {item.name}')
                os.remove(item_path)
                continue
        if item.is_dir():
            if item_time < critical_time:
                celery_log.info(f'deleting dir: {item.name}')
                shutil.rmtree(item_path)
    return {'state': 'ok'}
