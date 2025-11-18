import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()
import uvicorn
import os
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastapi.middleware.cors import CORSMiddleware
from endpoints.mqtt import mqtt_router
from endpoints.services import server_router
from endpoints.mcp import mcp_router
from middlewares.init_lifespan import tai_middleware

app = FastAPI(lifespan=tai_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(mqtt_router, prefix="/mqtt")
# app.include_router(server_router, prefix="/server")
app.include_router(mcp_router)

mcp = FastApiMCP(
    app,
    name="Worker Database MCP Tools",
    description="仅为 mcp_router 下的接口生成工具",
    include_operations=["get_worker_info", "post_attendance_by_date", "post_position_person_info",
                        "get_worker_attendance_last_month", "get_worker_field_routes_by_date", "get_environment_sensor_data",
                        "get_worker_questions_answers"]
)

mcp.mount_http()



if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=int((os.getenv("SERVER_PORT"))))