import asyncio

async def asyncify(func, *args, **kwargs):
    coro = asyncio.to_thread(func, *args, **kwargs)
    result = await coro
    return result
