import os
import json
import asyncio
from fastapi import APIRouter, Request
from endpoints.http_request_models import LightControlModel
from endpoints.mqtt_request_models import SensorDataModel

mqtt_router = APIRouter()
WAIT_SECONDS = int(os.getenv("MQTT_WAITTIME"))


@mqtt_router.get("/light-status", tags=["light-status"])
async def light_status(request: Request):
    mqtt_client = request.app.state.mqtt_client
    try:
        await asyncio.wait_for(mqtt_client.message_event["light-control"].wait(), WAIT_SECONDS)
        lock = asyncio.Lock()
        async with lock:
            mqtt_client.message_event["light-control"].clear()
            msg = mqtt_client.message_dict["light-control"]
            mqtt_client.message_dict["light-control"] = None
        return {"status": "success", "message": msg}
    except asyncio.TimeoutError:
        return {"status": "error", "message": "timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mqtt_router.post("/light-control", tags=["light-control"])
async def light_control(request: Request, light_model: LightControlModel):
    mqtt_client = request.app.state.mqtt_client
    try:
        await mqtt_client.publish("light-control", light_model.model_dump_json())
        return {"status": "success", "message": None}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mqtt_router.post("/sensor-data", tags=["light-control"])
async def sensor_data(request: Request):
    mqtt_client = request.app.state.mqtt_client
    function_name = "sensor-data"
    try:
        await asyncio.wait_for(mqtt_client.message_event[function_name].wait(), WAIT_SECONDS)
        lock = asyncio.Lock()
        async with lock:
            mqtt_client.message_event[function_name].clear()
            msg = json.loads(mqtt_client.message_dict[function_name])
            mqtt_client.message_dict[function_name] = None
        valid_data_format = SensorDataModel(**msg)
        await request.app.state.queue.put(msg)
        item = await asyncio.wait_for(request.app.state.queue.get(), timeout=WAIT_SECONDS)
        return {"status": "success", "message": item}
    except asyncio.TimeoutError:
        return {"status": "error", "message": "timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}




