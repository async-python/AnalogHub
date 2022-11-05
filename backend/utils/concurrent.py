import asyncio
from concurrent.futures.process import ProcessPoolExecutor


async def run_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        return await loop.run_in_executor(
            pool, func, *args)
