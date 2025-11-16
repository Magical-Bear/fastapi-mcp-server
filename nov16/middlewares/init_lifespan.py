import json
from fastapi import FastAPI
from datetime import timedelta, datetime
from contextlib import asynccontextmanager
import asyncio

from services.mqtt_client import AsyncIOMQTTService

@asynccontextmanager
async def tai_middleware(app: FastAPI):
    """
    FastAPI 应用的 lifespan 管理器，负责初始化和清理资源。

    :param app: FastAPI 应用实例
    """
    # 初始化资源
    mqtt_client = AsyncIOMQTTService()
    await mqtt_client.start()
    app.state.mqtt_client = mqtt_client

    queue = asyncio.Queue(10)
    app.state.queue = queue
    # await asyncio.sleep(10)
    # await mqtt_service.publish("light-control", "20")
    try:
        yield  # 应用运行期间
    finally:
        await mqtt_client.stop()
    # scheduler = AsyncIOScheduler()
    #
    # redis = await redis_connect()
    # app.state.redis = redis
    #
    # mysql = AsyncDatabase()
    # app.state.mysql = await mysql.get_sessions()
    # app.state.db_manager = mysql
    #
    # scheduler.add_job(update_server_functions,
    #                   IntervalTrigger(hours=24),
    #                   next_run_time=datetime.now(),
    #                   kwargs={"manage_mysql": app.state.manage_mysql, "redis_client": redis},  # 参数通过 kwargs 传
    #                   )
    #
    # scheduler.add_job(update_devices_info,
    #                   IntervalTrigger(hours=24),
    #                   next_run_time=datetime.now(),
    #                   kwargs={"manage_mysql": app.state.manage_mysql, "redis_client": redis}
    #                   )
    # scheduler.start()
    #
    # await db_conn_test(app.state.mysql)
    # try:
    #     yield  # 应用运行期间
    # finally:
    #     await app.state.redis.close()
    #     scheduler.shutdown()
    #     await mysql.dispose()
    #     print("redis 关闭")





