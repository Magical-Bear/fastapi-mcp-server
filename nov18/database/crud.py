import asyncio
import os
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, not_, outerjoin, select, insert, update, func, literal_column, case, desc

from database.models import AIQATable, WorkersTable, RFIDDevicesTable, RFIDDetectCardTable, CardsTable, WorkersLoginTable


async def db_get_workers_questions(session: AsyncSession, num: int = 10):
    stmt = (
        select(AIQATable.url, AIQATable.question, AIQATable.answer)
        .order_by(desc(AIQATable.create_time))
        .limit(num)
    )
    result = await session.execute(stmt)
    rows = result.all()  # 每行是 (url, question, answer)

    return [
        {"url": f"http://{os.getenv('BASE_URL')}:{os.getenv('PORT')}/mine_add/videos?filename={url}", "question": question, "answer": answer}
        for url, question, answer in rows
    ]


async def db_insert_workers_question(session: AsyncSession, records: list[dict]):
    if records:
        stmt = insert(AIQATable).values(records)
        await session.execute(stmt)
        await session.commit()


async def db_get_workers_route(session: AsyncSession, worker_id: int, day: date):
    day_min = datetime.combine(day, datetime.min.time())
    day_max = datetime.combine(day, datetime.max.time())

    query = (
        select(
            RFIDDevicesTable.position,
            RFIDDetectCardTable.create_time
        )
        .select_from(RFIDDetectCardTable)
        .join(RFIDDevicesTable, RFIDDetectCardTable.device_id == RFIDDevicesTable.id)
        .join(CardsTable, CardsTable.id == RFIDDetectCardTable.card_id)
        .join(WorkersTable, WorkersTable.id == CardsTable.worker_id)
        .where(WorkersTable.id == worker_id)
        .where(RFIDDetectCardTable.create_time > day_min)
        .where(RFIDDetectCardTable.create_time < day_max)
    )
    results = await session.execute(query)
    records = list({x[0]: x for x in reversed(results.all())}.values())[::-1]
    return {
        str(i): {
            "位置": data[0],
            "时间": data[1]
        } for i, data in enumerate(records)
    }


async def db_get_worker_month_attendance(session: AsyncSession, worker_id: int):
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=31)

    stmt = (
        select(
            WorkersLoginTable.create_time
        )
        .where(
        WorkersLoginTable.worker_id == worker_id,
        WorkersLoginTable.create_time >= thirty_days_ago,
        WorkersLoginTable.create_time <= now
        )
        .order_by(WorkersLoginTable.create_time.desc()))

    result = await session.execute(stmt)
    records = result.scalars().all()  # 提取 ORM 实例列表

    return records


async def db_get_date_position_person(session: AsyncSession, position_id: int, day: date):
    day_min = datetime.combine(day, datetime.min.time())
    day_max = datetime.combine(day, datetime.max.time())

    query = (
        select(
            RFIDDetectCardTable.card_id
        )
        .select_from(CardsTable)
        .join(RFIDDetectCardTable, RFIDDetectCardTable.card_id == CardsTable.id)
        .where(RFIDDetectCardTable.device_id == position_id)
        .where(RFIDDetectCardTable.create_time >= day_min)
        .where(RFIDDetectCardTable.create_time <= day_max)
    )
    results = await session.execute(query)
    results = list(set(data[0] for data in results))
    return results



async def db_get_date_attendance(session: AsyncSession, day_list: list[date]):
    task_list = []
    for day in day_list:
        day_min = datetime.combine(day, datetime.min.time())
        day_max = datetime.combine(day, datetime.max.time())

        query = (
            select
                (
                    WorkersTable.name,
                    WorkersLoginTable.create_time,
                )
            .select_from(WorkersLoginTable)
            .join(WorkersTable, WorkersTable.id == WorkersLoginTable.worker_id)
            .where(WorkersLoginTable.create_time >= day_min)
            .where(WorkersLoginTable.create_time <= day_max)
        )
        task_list.append(session.execute(query))
    results = await asyncio.gather(*task_list)
    results_dict = {}
    if len(results) != 0:
        for i, result in enumerate(results):
            if result:
                results_dict[day_list[i].strftime("%Y-%m-%d")] = [(data[0], data[1].strftime("%H:%M:%S"))for data in result.all()]
            else:
                results_dict[day_list[i].strftime("%Y-%m-%d")] = []
    return results_dict


async def db_get_worker_info(session: AsyncSession, worker_name: str):
    today = date.today()
    query = (
        select(
            WorkersTable.id,
            WorkersTable.name,
            WorkersTable.gender,
            WorkersTable.birthday,
        )
        .where(WorkersTable.name == worker_name)
    )
    result = await session.execute(query)
    result = result.all()
    if result:
        result = result[0]
        age, month = divmod((today.year - result[3].year) * 12 + (today.month - result[3].month), 12)
        return {
            "工号": result[0],
            "姓名": result[1],
            "性别": "男" if result[2] == 1 else "女",
            "出生日期": result[3].strftime("%Y-%m-%d"),
            "年龄": f"{age}岁余{month}月"
        }
    return {}


# async def db_get_date_human_is_arrival(session: AsyncSession, day: date, worker_name: str):
#     query = (
#         select
#             (
#                 WorkersTable.name,
#                 WorkersLoginTable.create_time,
#             )
#         .select_from(WorkersTable)
#         .join(WorkersLoginTable, WorkersTable.id == WorkersLoginTable.worker_id)
#         .where(WorkersTable.name == worker_name)
#         .where(WorkersLoginTable.create_time == date.today())
#     )
#     result = await session.execute(query)
#     result = result.all()

async def get_devices_id(session: AsyncSession):
    query = (
        select(RFIDDevicesTable.id,
               RFIDDevicesTable.mac,
               RFIDDevicesTable.position)
        .where(or_(RFIDDevicesTable.is_stop != 1, RFIDDevicesTable.is_stop.is_(None)))
    )

    results = await session.execute(query)
    results = {data[0]: {"mac": data[1], "position": data[2]} for data in results.all()}
    return results


async def get_cards_id(session: AsyncSession):
    query = (
        select(CardsTable.id,
               CardsTable.card_id,
               CardsTable.worker_id
                )
        .where(or_(CardsTable.is_stop != 1, CardsTable.is_stop.is_(None)))
    )
    results = await session.execute(query)
    results = {data[0]: {"card_sn": data[1], "worker_id": data[2]} for data in results.all()}
    return results


async def get_workers_id(session: AsyncSession):
    query = (
        select(
            WorkersTable.id,
            WorkersTable.name,
            WorkersTable.gender
        )
        .where(or_(WorkersTable.is_stop != 1, WorkersTable.is_stop.is_(None)))
    )
    results = await session.execute(query)
    results = {data[0]: {"worker_name": data[1], "worker_gender": "男" if data[2] == 1 else "女"} for data in results.all()}
    return results


async def detect_card_submit(session: AsyncSession, device_id: int, cards_id: list[int]):
    values = [
        {
            "device_id": device_id,
            "card_id": card_id
        }
        for card_id in cards_id
    ]

    if values:
        stmt = insert(RFIDDetectCardTable).values(values)
        await session.execute(stmt)
        await session.commit()


async def login_data_submit(session: AsyncSession, workers_id_list: list[dict]):
    stmt = insert(WorkersLoginTable).values(workers_id_list)
    await session.execute(stmt)
    await session.commit()


async def worker_position_select(session: AsyncSession, day: date) -> dict | None:
    day_min = datetime.combine(day, datetime.min.time())
    day_max = datetime.combine(day, datetime.max.time())

    query = (
        select(
                RFIDDetectCardTable.card_id,
                RFIDDevicesTable.position,
                RFIDDetectCardTable.create_time
               )
        .select_from(RFIDDetectCardTable)
        .join(RFIDDevicesTable, RFIDDetectCardTable.device_id == RFIDDevicesTable.id)
        .where(RFIDDetectCardTable.create_time > day_min)
        .where(RFIDDetectCardTable.create_time < day_max)
        .group_by(RFIDDetectCardTable.card_id, RFIDDevicesTable.position, RFIDDetectCardTable.create_time)
    )

    result = await session.execute(query)
    rows = result.all()  # 每行是 (url, question, answer)
    if len(rows) == 0:
        return None
    card_id_set = set([item[0]for item in rows])

    query = (
        select(CardsTable.id, WorkersTable.name)
        .select_from(WorkersTable)
        .join(CardsTable, CardsTable.worker_id == WorkersTable.id)
        .where(WorkersTable.id.in_(card_id_set))
    )
    result = await session.execute(query)
    persons = result.all()  # 每行是 (url, question, answer)
    workers_positions_dict = {}
    for i in range(len(rows) -1, -1, -1):
        if rows[i][0] not in workers_positions_dict:
            workers_positions_dict[rows[i][0]] = {
                "name": [person[1] for person in persons if person[0] == rows[i][0]][0],
                "position": rows[i][1],
                "time": rows[i][2].strftime("%Y-%m-%d %H:%M:%S"),
            }
        else:
            continue
    return workers_positions_dict





