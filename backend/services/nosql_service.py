from abc import ABC, abstractmethod
from functools import lru_cache
from http import HTTPStatus
from typing import Any, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException
from fastapi.logger import logger

from core.config import AppSettings
from db.elastic_db import get_elastic
from models.es_models.es_analog import DataAnalogIn
from models.es_models.es_tool import DataToolIn
from utils.concurrent import run_in_executor
from utils.enums import Maker, SearchType
from utils.file_utils import get_base_names_xlsx, save_xlsx_analogs
from utils.queries import (get_multimatch_query, get_pagination_query,
                           page_search_params)
from utils.transliterate import prepare_text, stringify

settings = AppSettings()


class NosqlServiceMixin:

    def __init__(self, elastic: AsyncElasticsearch,
                 model: Any, es_index: str):
        self.elastic = elastic
        self.model = model
        self.es_index = es_index

    async def get_list_from_elastic(
            self, page_number: int, page_size: int,
            query: dict = None, es_index=None, model=None):
        if not es_index:
            es_index = self.es_index
        if not model:
            model = self.model
        body = get_pagination_query(page_number, page_size)
        try:
            if query:
                body = body | query
            docs = await self.elastic.search(
                index=es_index,
                body=body
            )
        except Exception as error:
            logger.info(error)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='bad request')
        if not len(docs['hits']['hits']):
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail='not found')
        return [model(**doc['_source']) for doc in
                docs['hits']['hits']]

    async def get_obj_from_elastic(self, obj_id: str):
        result = await self.elastic.exists(index=self.es_index, id=obj_id)
        if result:
            doc = await self.elastic.get(index=self.es_index, id=obj_id)
            return self.model(**doc['_source'])
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='not found')


class AbstractNosqlService(ABC):

    @abstractmethod
    async def search_list_analogs(self, file_path, result_file_path):
        ...

    @abstractmethod
    async def search_analogs_ngram(self, request: str,
                                   page_number: int, page_size: int,
                                   search_fields: list[str] = None,
                                   ):
        ...

    @abstractmethod
    async def search_analogs_string(self, request: str,
                                    page_number: int, page_size: int,
                                    search_fields: list[str] = None,
                                    ) -> Optional[list[DataAnalogIn]]:
        ...

    @abstractmethod
    async def search_products_ngram(self, request: str, maker: Maker,
                                    page_number: int, page_size: int
                                    ) -> Optional[list[DataToolIn]]:
        ...

    @abstractmethod
    async def search_products_wildcard(self, request: str, maker: Maker,
                                       page_number: int, page_size: int
                                       ) -> Optional[list[DataToolIn]]:
        ...


class NosqlService(AbstractNosqlService, NosqlServiceMixin):
    async def search_list_analogs(self, file_path, result_file_path):
        base_names = await run_in_executor(get_base_names_xlsx, file_path)
        analogs, analog_makers, bad = [], [], []
        for i, text in enumerate(base_names):
            try:
                prepared_text = prepare_text(text)
                if len(prepared_text):
                    prepared_text = stringify(prepared_text)
                    analog = await self.search_analogs_string(
                        prepared_text, **page_search_params,
                        search_fields=['base_name_string'])
                    analogs.append(analog[0].analog_name)
                    analog_makers.append(analog[0].analog_maker)
                else:
                    analogs.append(None)
                    analog_makers.append(None)
            except HTTPException:
                bad.append(i)
                analog = await self.search_analogs_ngram(
                    text, search_fields=['base_name_ngram'],
                    **page_search_params)
                analogs.append(analog[0].analog_name)
                analog_makers.append(analog[0].analog_maker)
        await run_in_executor(
            save_xlsx_analogs, file_path, result_file_path,
            analogs, analog_makers, bad)

    async def search_analogs_ngram(self, request: str,
                                   page_number: int, page_size: int,
                                   search_fields: list[str] = None,
                                   ) -> Optional[list[DataAnalogIn]]:
        if search_fields is None:
            search_fields = ['analog_name_ngram', 'base_name_ngram']
        query = get_multimatch_query(search_fields, request)
        analogs = await self.get_list_from_elastic(page_number,
                                                   page_size, query)
        return analogs

    async def search_analogs_string(self, request: str,
                                    page_number: int, page_size: int,
                                    search_fields: list[str] = None,
                                    ) -> Optional[list[DataAnalogIn]]:
        if search_fields is None:
            search_fields = ['analog_name_string', 'base_name_string']
        query = get_multimatch_query(
            search_fields, request, SearchType.query_string)
        analogs = await self.get_list_from_elastic(page_number,
                                                   page_size, query)
        return analogs

    async def search_products_ngram(self, request: str, maker: Maker,
                                    page_number: int, page_size: int
                                    ) -> Optional[list[DataToolIn]]:
        search_fields = ['name_ngram', 'search_field']
        if maker.value != Maker.ALL:
            query = get_multimatch_query(
                search_fields, request, maker.value)
        else:
            query = get_multimatch_query(search_fields, request)
        products = await self.get_list_from_elastic(
            page_number,
            page_size, query,
            es_index=settings.es_index_product,
            model=DataToolIn)
        return products

    async def search_products_wildcard(self, request: str, maker: Maker,
                                       page_number: int, page_size: int
                                       ) -> Optional[list[DataToolIn]]:
        search_fields = ['name_string', ]
        if maker.value != Maker.ALL:
            query = get_multimatch_query(
                search_fields, request, maker.value, SearchType.query_string)
        else:
            query = get_multimatch_query(
                search_fields, request, SearchType.query_string)
        products = await self.get_list_from_elastic(
            page_number, page_size, query,
            es_index=settings.es_index_product,
            model=DataToolIn)
        return products


# Depend
@lru_cache()
def get_nosql_service(
        elastic: AsyncElasticsearch = Depends(
            get_elastic), ) -> NosqlService:
    return NosqlService(elastic, DataAnalogIn, 'analog')
