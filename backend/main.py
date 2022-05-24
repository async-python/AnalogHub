import logging

import uvicorn
from api.v1 import analogs
from core.config import AppSettings
from core.logger import LOGGING
from db import elastic
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.responses import RedirectResponse

settings = AppSettings()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)


@app.get('/')
async def index():
    return RedirectResponse('/api/openapi', status_code=status.HTTP_302_FOUND)


@app.on_event('startup')
async def startup():
    elastic.es = AsyncElasticsearch(hosts=settings.elastic_url)


@app.on_event('shutdown')
async def shutdown():
    await elastic.es.close()


app.include_router(analogs.router, prefix='/api/v1/analog',
                   tags=['Search Analogs'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
