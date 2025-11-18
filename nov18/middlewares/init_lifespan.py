import json
import asyncio
from fastapi import FastAPI
from datetime import timedelta, datetime
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from services.mqtt_client import AsyncIOMQTTService
from database.fastapi_sqlalchemy import AsyncDatabase
from utils.timer_tasks import broadcast_worker_position


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

    mysql = AsyncDatabase()
    app.state.db = await mysql.get_sessions()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(broadcast_worker_position,
                      IntervalTrigger(minutes=1),
                      next_run_time=datetime.now(),
                      kwargs={"app": app},  # 参数通过 kwargs 传
                      )
    scheduler.start()

    try:
        yield  # 应用运行期间
    finally:
        scheduler.shutdown()
        await mqtt_client.stop()
        await mysql.dispose()






