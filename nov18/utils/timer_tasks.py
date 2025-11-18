import os
import json
from fastapi import FastAPI
from datetime import datetime, date

from database.crud import worker_position_select


async def broadcast_worker_position(app: FastAPI):
    sessionmaker = app.state.db["mine"]
    async with sessionmaker() as session:
        position_broadcast = await worker_position_select(session, date.today())
    print(position_broadcast)
    # topic = os.getenv("WORKER_POSITION_BROADCAST_TOPIC")
    # payload = position_broadcast or {}
    #
    # # 发布消息
    # await app.state.mqtt_client.publish(topic, json.dumps(payload, ensure_ascii=False).encode())