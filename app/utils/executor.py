import asyncio

async def run_in_thread(func: Callable[..., Any], *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        partial(func, *args, **kwargs),
    )