from functools import lru_cache
from typing import Optional

from core.config import AppSettings
from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException
from models.input.model_analog import DataAnalogEntry
from models.input.model_product import DataProductEntry
from services.concurrent import run_in_executor
from services.enums import Maker, SearchType
from services.file_utils import get_base_names_xlsx, save_xlsx_analogs
from services.queries import (get_multimatch_query,
                              page_search_params)
from services.template_service import TemplateService
from services.transliterate import prepare_text, stringify

settings = AppSettings()


class AnalogService(TemplateService):
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
                                   ) -> Optional[list[DataAnalogEntry]]:
        if search_fields is None:
            search_fields = ['analog_name_ngram', 'base_name_ngram']
        query = get_multimatch_query(search_fields, request)
        analogs = await self.get_list_from_elastic(page_number,
                                                   page_size, query)
        return analogs

    async def search_analogs_string(self, request: str,
                                    page_number: int, page_size: int,
                                    search_fields: list[str] = None,
                                    ) -> Optional[list[DataAnalogEntry]]:
        if search_fields is None:
            search_fields = ['analog_name_string', 'base_name_string']
        query = get_multimatch_query(
            search_fields, request, SearchType.query_string)
        analogs = await self.get_list_from_elastic(page_number,
                                                   page_size, query)
        return analogs

    async def search_products_ngram(self, request: str, maker: Maker,
                                    page_number: int, page_size: int
                                    ) -> Optional[list[DataProductEntry]]:
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
            model=DataProductEntry)
        return products

    async def search_products_wildcard(self, request: str, maker: Maker,
                                       page_number: int, page_size: int
                                       ) -> Optional[list[DataProductEntry]]:
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
            model=DataProductEntry)
        return products


@lru_cache()
def get_analog_service(
        elastic: AsyncElasticsearch = Depends(
            get_elastic), ) -> AnalogService:
    return AnalogService(elastic, DataAnalogEntry, 'analog')
