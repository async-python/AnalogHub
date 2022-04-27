from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from core.config import AppSettings
from db.elastic import get_elastic
from models.input.model_analog import DataAnalogEntry
from models.input.model_product import DataProductEntry
from services.makers.choices import Maker
from services.template_service import TemplateService
from services.utils import get_multimatch_query, get_wildcard_query

settings = AppSettings()


class AnalogService(TemplateService):
    async def search_analogs_ngram(self, request: str,
                                   page_number: int, page_size: int
                                   ) -> Optional[list[DataAnalogEntry]]:
        search_fields = ['analog_name_ngram', 'base_name_ngram']
        query = get_multimatch_query(search_fields, request)
        analogs = await self.get_list_from_elastic(page_number,
                                                   page_size, query)
        return analogs

    async def search_analogs_string(self, request: str,
                                    page_number: int, page_size: int
                                    ) -> Optional[list[DataAnalogEntry]]:
        search_fields = ['analog_name_string', 'base_name_string']
        query = get_wildcard_query(search_fields, request)
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
            query = get_wildcard_query(search_fields, request, maker)
        else:
            query = get_wildcard_query(search_fields, request)
        products = await self.get_list_from_elastic(
            page_number,
            page_size, query,
            es_index=settings.es_index_product,
            model=DataProductEntry)
        return products


@lru_cache()
def get_analog_service(
        elastic: AsyncElasticsearch = Depends(
            get_elastic), ) -> AnalogService:
    return AnalogService(elastic, DataAnalogEntry, 'analog')
