from uuid import UUID

from fastapi import APIRouter, Depends, Query

from models.error_model import Message404
from models.ps_models.tool_models import (ListToolIn, ListToolInDel,
                                          ToolCreated, ToolDeleted, ToolFull,
                                          ToolIn, ToolUpdated)
from services.sql_service import SqlService, get_sql_service

router = APIRouter()


async def common_parameters(page_num: int = Query(default=0, ge=0),
                            page_size: int = Query(default=10, gt=0)):
    return {'page_num': page_num, 'page_size': page_size}


async def search_parameters(title: str = Query(default='', min_length=1),
                            maker: str = Query(default='',
                                               min_length=1)):
    return {'title': title, 'maker': maker}


@router.get('/tools/', response_model=list[ToolFull])
async def get_tools(params=Depends(common_parameters),
                    sql_service: SqlService = Depends(get_sql_service)):
    return await sql_service.get_tools(**params)


@router.get('/tool/', response_model=ToolFull,
            responses={404: {'model': Message404}})
async def get_tool(params=Depends(search_parameters),
                   sql_service: SqlService = Depends(get_sql_service)):
    return await sql_service.get_tool(**params)


@router.post('/tool', response_model=ToolCreated)
async def create_tool(tool: ToolIn,
                      sql_service: SqlService = Depends(get_sql_service)):
    return await sql_service.create_tool(tool)


@router.put('/tool', response_model=ToolUpdated,
            responses={404: {'model': Message404}})
async def update_tool(tool: ToolIn,
                      sql_service: SqlService = Depends(get_sql_service)):
    return await sql_service.update_tool(tool)


@router.delete('/tool', response_model=ToolDeleted)
async def delete_tool(uuid: UUID,
                      sql_service: SqlService = Depends(get_sql_service)):
    return await sql_service.delete_tool(uuid)


@router.post('/tool_bulk', response_model=ToolCreated)
async def create_tool_bulk(body: ListToolIn,
                           sql_service: SqlService = Depends(get_sql_service)):
    return await sql_service.create_tool_bulk(body.tools)


@router.put('/tool_bulk', response_model=ToolCreated,
            responses={404: {'model': Message404}})
async def update_tool_bulk(tools: ListToolIn,
                           sql_service: SqlService = Depends(get_sql_service)):
    return await sql_service.update_tool_bulk(tools.tools)


@router.delete('/tool_bulk', response_model=ToolDeleted)
async def delete_tool_bulk(body: ListToolInDel,
                           sql_service: SqlService = Depends(get_sql_service)):
    return await sql_service.delete_tool_bulk(body.ids)
