import asyncio
import aiomqtt
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    async with aiomqtt.Client("139.9.68.120") as client:
        await client.publish("temperature/outside", payload=28.4)


asyncio.run(main())