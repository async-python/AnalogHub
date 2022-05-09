from http import HTTPStatus
from typing import Any

from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException
from fastapi.logger import logger

from services.queries import get_pagination_query


class TemplateService:

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
            logger.info(query)
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
