import os
from http import HTTPStatus

import celery
import fastapi
from celery.result import AsyncResult
from fastapi import (APIRouter, BackgroundTasks, Depends, File, Query,
                     UploadFile, HTTPException)
from starlette.responses import FileResponse, JSONResponse

from core.config import BASE_DIR
from models.out.model_analog_out import DataAnalogOut
from models.out.model_product_out import DataProductOut
from services.analog_service import AnalogService, get_analog_service
from services.concurrent import run_in_executor
from services.file_utils import (get_xlsx_path, save_file, verify_xlsx_type,
                                 verify_zip_type, xlsx_headers,
                                 verify_required_fields)
from services.enums import Filter, Maker, Table
from services.queries import page_num_params, page_size_params
from services.transliterate import prepare_text
from worker import (get_task_result, upload_elastic_analogs,
                    upload_elastic_makers)

router = APIRouter()


@router.get('/tasks/{task_id}')
def get_status(task_id: str):
    task_result: AsyncResult = get_task_result(task_id)
    result = {
        'task_id': task_id,
        'task_status': task_result.status,
        'task_result': task_result.result
    }
    return JSONResponse(result)


@router.post('/search_list_analogs',
             name='Поиск списка аналогов инструмента',
             description='Полнотекстовый поиск писков аналогов инструмента. '
                         'Требуется xlsx файл с полями: '
                         f'"{Table.tool}", "{Table.brand}"',
             response_description='xlsx',
             response_class=File(...),
             status_code=201)
async def search_list_analogs(background_tasks: BackgroundTasks,
                              xlsx_file: UploadFile = File(...),
                              analog_service: AnalogService = Depends(
                                  get_analog_service)):
    verify_xlsx_type(xlsx_file)
    file_path, result_file_path = get_xlsx_path(), get_xlsx_path()
    await save_file(xlsx_file, file_path)

    verify = await run_in_executor(
        verify_required_fields, file_path, [Table.tool, Table.brand])
    if not verify:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f'bad request')

    await analog_service.search_list_analogs(file_path, result_file_path)
    background_tasks.add_task(os.remove, file_path)
    background_tasks.add_task(os.remove, result_file_path)
    return FileResponse(result_file_path, headers=xlsx_headers)


@router.post('/search_analog',
             name='Поиск аналога инструмента',
             description='Полнотекстовый поиск аналога инструмента',
             response_model=list[DataAnalogOut],
             response_model_exclude_none=True)
async def search_analogs(query: str,
                         search_type: Filter = Filter.ngram_search,
                         page_number: int = Query(**page_num_params),
                         page_size: int = Query(**page_size_params),
                         analog_service: AnalogService = Depends(
                             get_analog_service)) -> list[DataAnalogOut]:
    query_text = prepare_text(query)
    if search_type == Filter.ngram_search:
        result = await analog_service.search_analogs_ngram(
            query_text, page_number, page_size)
    else:
        result = await analog_service.search_analogs_string(
            query_text, page_number, page_size)
    return [DataAnalogOut(**model.dict()) for model in result]


@router.post('/search_product',
             name='Поиск инструмента по производителю',
             description='Полнотекстовый поиск инструмента по производителю',
             response_model=list[DataProductOut],
             response_model_exclude_none=True)
async def search_products(query: str,
                          search_type: Filter = Filter.ngram_search,
                          maker: Maker = Maker.ALL,
                          page_number: int = Query(**page_num_params),
                          page_size: int = Query(**page_size_params),
                          analog_service: AnalogService = Depends(
                              get_analog_service)) -> list[DataProductOut]:
    query_text = prepare_text(query)
    if search_type == Filter.ngram_search:
        result = await analog_service.search_products_ngram(
            query_text, maker, page_number, page_size)
    else:
        result = await analog_service.search_products_wildcard(
            query_text, maker, page_number, page_size)
    return [DataProductOut(**model.dict()) for model in result]


@router.post('/upload_analogs',
             name='Загрузка таблиц аналогов',
             description='Требуется xlsx файл с полями: '
                         '"Инструмент", "Бренд", "Аналог", "Бренд аналога"',
             status_code=201)
async def upload_analogs_xlsx(xlsx_file: UploadFile = File(...)):
    verify_xlsx_type(xlsx_file)
    file_path = get_xlsx_path()
    await save_file(xlsx_file, file_path)

    fields = [x.value for x in [*Table]]
    verify = await run_in_executor(
        verify_required_fields, file_path, fields)
    if not verify:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f'bad request')

    task: celery.Task = upload_elastic_analogs.delay(file_path=file_path)
    return {'result': 'acknowledge True', 'task_id': task.id}


@router.post('/upload_makers',
             name='Загрузка прайсов производителей',
             description='Загрузка прайсов производителей zip архивом',
             status_code=201)
async def upload_makers_zip(zip_file: UploadFile = File(...)):
    verify_zip_type(zip_file)
    file_name = zip_file.filename
    file_path = str(BASE_DIR.joinpath('file_storage') / file_name)
    await save_file(zip_file, file_path)
    task: celery.Task = upload_elastic_makers.delay(
        file_path=file_path, file_name=file_name)
    return {'result': 'acknowledge True', 'task_id': task.id}
