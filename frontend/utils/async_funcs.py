import asyncio

import aiofiles
import aiohttp
from aiohttp import FormData

from core.conf import BASE_DIR
from utils.choices import Response_type
from utils.data_models import HTTPResponse

content_types = {
    'xlsx_file': 'application/vnd.openxmlformats-officedocument.'
                 'spreadsheetml.sheet',
    'zip_file': 'application/zip'
}


async def fetch(url, params):
    async with aiohttp.ClientSession(loop=asyncio.get_event_loop()) as session:
        async with session.post(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status
            )


async def fetch_file(url: str, file_path: str, file_name: str, file_type: str,
                     resp_type: Response_type = Response_type.Json):
    async with aiohttp.ClientSession(loop=asyncio.get_event_loop()) as session:
        data = FormData()
        data.add_field(file_type, await aiofiles.open(file_path, 'rb'),
                       filename=file_name,
                       content_type=content_types.get(file_type))
        async with session.post(url, data=data) as response:
            if resp_type == Response_type.Json:
                return HTTPResponse(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status
                )
            else:
                if response.status == 200:
                    response_filename = 'response.xlsx'
                    response_path = BASE_DIR.joinpath(
                        'static') / response_filename
                    f = await aiofiles.open(response_path, mode='wb')
                    await f.write(await response.read())
                    await f.close()
                return response_filename
