import asyncio


async def run_task():
    await asyncio.sleep(1)
    print('任务完成...')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_task())
