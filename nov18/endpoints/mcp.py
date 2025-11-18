from datetime import date
from fastapi import APIRouter, Request
from database.crud import get_workers_id, get_devices_id, db_get_workers_questions, db_get_workers_route, db_get_worker_month_attendance, db_get_date_position_person, db_get_worker_info, db_get_date_attendance
from endpoints.mcp_request_models import DateModel, PositionModel


mcp_router = APIRouter()


@mcp_router.get("/worker-info", tags=["获取工人信息"], operation_id="get_worker_info")
async def get_worker_info(request: Request, worker_name: str):
    sessionmaker = request.app.state.db["mine"]
    async with sessionmaker() as session:
        return await db_get_worker_info(session, worker_name)


@mcp_router.post("/attendance-info", tags=["获取特定日期的人员到岗情况"], operation_id="post_attendance_by_date")
async def get_attendance_info(request: Request, date_model: DateModel):
    sessionmaker = request.app.state.db["mine"]
    async with sessionmaker() as session:
        return await db_get_date_attendance(session, date_model.date_list)


@mcp_router.post("/get-position-person-info", tags=["获取指定位置指定日期的人员情况"], operation_id="post_position_person_info")
async def get_position_person_info(request: Request, position_model: PositionModel):
    sessionmaker = request.app.state.db["mine"]
    async with sessionmaker() as session:
        devices_table = await get_devices_id(session)
        device_id = [k for k, v in devices_table.items() if v["position"] == position_model.position]
        if not device_id:
            return {"error": "不存在的区域名"}
        results_info = {"人员姓名": [], "人员数目": 0}
        person_id_list = await db_get_date_position_person(session, device_id[0], position_model.day)
        if person_id_list:
            workers_table = await get_workers_id(session)
            person_name_list = [workers_table[id]["worker_name"] for id in person_id_list]
            results_info["人员姓名"] = person_name_list
            results_info["人员数目"] = len(person_name_list)
    return results_info


@mcp_router.get("/get-worker-attendance-info", tags=["获取工人近一月的考勤信息"], operation_id="get_worker_attendance_last_month")
async def get_worker_attendance_info(request: Request, worker_name: str):
    sessionmaker = request.app.state.db["mine"]
    async with sessionmaker() as session:
        workers_table = await get_workers_id(session)
        worker_id = [k for k, v in workers_table.items() if v["worker_name"] == worker_name]
        if not worker_id:
            return {"error": "不存在的人员"}
        records = await db_get_worker_month_attendance(session, worker_id[0])
        return records


@mcp_router.get("/get-worker-field-router", tags=["获取在特定日期下的工人行动轨迹"], operation_id="get_worker_field_routes_by_date")
async def get_worker_field_router(request: Request, worker_name: str, day: date):
    sessionmaker = request.app.state.db["mine"]
    async with sessionmaker() as session:
        workers_table = await get_workers_id(session)
        worker_id = [k for k, v in workers_table.items() if v["worker_name"] == worker_name]
        if not worker_id:
            return {"error": "不存在的人员"}
        return await db_get_workers_route(session, worker_id[0], day)


@mcp_router.get("/get-env-sensor-data", tags=["获取环境传感器数据列表"], operation_id="get_environment_sensor_data")
async def get_environment_sensor_data(request: Request):
    data = await request.app.state.shared.get("sensor-data")
    if not data:
        data = {
            "temperature": [26],
            "humidity": [62],
            "methane": [10]
        }
    return data


@mcp_router.get("/get-worker-questions-answers", tags=["获取工人询问的问题情况"], operation_id="get_worker_questions_answers")
async def get_worker_questions_answers(request: Request):
    sessionmaker = request.app.state.db["mine"]
    async with sessionmaker() as session:
        records = await db_get_workers_questions(session)
    return {"records": records}