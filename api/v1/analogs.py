import uuid

import aiofiles
import celery
from celery.result import AsyncResult
from fastapi import (APIRouter, BackgroundTasks, Depends, File, HTTPException,
                     Query, UploadFile)
from fastapi.logger import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from core.config import BASE_DIR, templates
from models.input.model_analog import DataAnalogEntry
from models.input.model_product import DataProductEntry
from services.analog_service import AnalogService, get_analog_service
from services.makers.choices import Maker
from services.transliterate import prepare_text
from services.utils import page_num_params, page_size_params
from worker import upload_elastic_analogs, upload_elastic_makers

router = APIRouter()

xlsx_con_type = ('application/vnd.openxmlformats'
                 '-officedocument.spreadsheetml.sheet')
zip_con_type = 'application/zip'


@router.get("/search_analog", response_class=HTMLResponse, tags=['html'])
async def search_item(request: Request,
                      analog_service: AnalogService = Depends(
                          get_analog_service)):
    body = request.query_params['query']
    response = await search_analogs(body, 0, 20, analog_service)
    return templates.TemplateResponse("index.html",
                                      {'request': request, 'result': response})


@router.post('/search_analog',
             name='Поиск аналога инструмента',
             description='Полнотекстовый поиск аналога инструмента',
             response_model=list[DataAnalogEntry],
             response_model_exclude_unset=True)
async def search_analogs(query: str,
                         page_number: int = Query(**page_num_params),
                         page_size: int = Query(**page_size_params),
                         analog_service: AnalogService = Depends(
                             get_analog_service)) -> list[DataAnalogEntry]:
    query_text = prepare_text(query)
    rows: list[DataAnalogEntry] = await analog_service.search_analogs(
        query_text, page_number, page_size)
    return rows


@router.post('/search_product',
             name='Поиск инструмента по производителю',
             description='Полнотекстовый поиск инструмента по производителю',
             response_model=list[DataProductEntry],
             response_model_exclude_unset=True)
async def search_products(query: str,
                          maker: Maker = Maker.ALL,
                          page_number: int = Query(**page_num_params),
                          page_size: int = Query(**page_size_params),
                          analog_service: AnalogService = Depends(
                              get_analog_service)) -> list[DataProductEntry]:
    query_text = prepare_text(query)
    rows: list[DataProductEntry] = await analog_service.search_products_wildcard(
        query_text, maker, page_number, page_size)
    return rows


@router.post('/upload_analogs', status_code=201)
async def upload_analogs_xlsx(xlsx_file: UploadFile = File(...),
                              base_col_num: int = 2,
                              base_maker_col_num: int = 3,
                              analog_col_num: int = 7,
                              analog_maker_col_num: int = 8):
    if xlsx_file.content_type != xlsx_con_type:
        raise HTTPException(400, detail='Invalid document type')
    logger.info('file opening')
    file_name = str(uuid.uuid4()) + '.xlsx'
    file_path = str(BASE_DIR.joinpath('file_storage') / file_name)
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(await xlsx_file.read())
    kwargs = {'base_col_num': base_col_num,
              'base_maker_col_num': base_maker_col_num,
              'analog_col_num': analog_col_num,
              'analog_maker_col_num': analog_maker_col_num}
    task: celery.Task = upload_elastic_analogs.delay(
        file_path=file_path, **kwargs)
    return {'result': 'acknowledge True', 'task_id': task.id}


@router.post('/upload_makers', status_code=201)
async def upload_makers_zip(zip_file: UploadFile = File(...)):
    if zip_file.content_type != zip_con_type:
        raise HTTPException(400, detail='Invalid document type')
    file_name = zip_file.filename
    file_path = str(BASE_DIR.joinpath('file_storage') / file_name)
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(await zip_file.read())
    task: celery.Task = upload_elastic_makers.delay(
        file_path=file_path, file_name=file_name)
    return {'result': 'acknowledge True', 'task_id': task.id}
