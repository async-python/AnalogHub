import logging

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import HTMLResponse

from api.v1 import analogs
from core.config import AppSettings, templates
from core.logger import LOGGING
from db import elastic

settings = AppSettings()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.get('/', response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
