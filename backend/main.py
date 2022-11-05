import logging

import databases
import uvicorn
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.responses import RedirectResponse, Response

from api.v1 import auth, manage, search
from core.config import AppSettings
from core.logger import LOGGING
from db import elastic_db, postgres_db, redis_db

logger = logging.getLogger(__name__)
settings = AppSettings()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)


@app.middleware('http')
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as error:
        logger.info(str(error))
        return Response('Internal server error', status_code=500)


@app.get('/')
async def index():
    return RedirectResponse('/api/openapi', status_code=status.HTTP_302_FOUND)


@app.on_event('startup')
async def startup():
    elastic_db.es = AsyncElasticsearch(hosts=settings.elastic_url)
    postgres_db.ps = databases.Database(settings.postgres_url)
    redis_db.rs = Redis(host=settings.redis_host,
                        port=settings.redis_port,
                        password=settings.redis_password,
                        decode_responses=True,
                        db=settings.redis_base)
    await postgres_db.ps.connect()


@app.on_event('shutdown')
async def shutdown():
    await elastic_db.es.close()
    await postgres_db.ps.disconnect()
    await redis_db.rs.close()


app.include_router(search.router, prefix='/api/v1/analog',
                   tags=['Search Analogs'])
app.include_router(manage.router, prefix='/api/v1/manage',
                   tags=['Manage Tools'])
app.include_router(auth.router, prefix='/api/v1/auth',
                   tags=['Auth Service'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
