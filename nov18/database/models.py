import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

tz_utc_8 = datetime.timezone(datetime.timedelta(hours=8))

class Base(MappedAsDataclass, DeclarativeBase):
    pass


class RFIDDetectCardTable(Base):
    __tablename__ = 'RFID_detect_card_table'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    device_id: Mapped[int] = mapped_column(Integer)
    card_id: Mapped[int] = mapped_column(Integer)
    update_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(tz_utc_8))



class RFIDDevicesTable(Base):
    __tablename__ = 'RFID_devices_table'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, comment='设备ID')
    mac: Mapped[str] = mapped_column(String(255, 'utf8mb4_general_ci'), comment='设备序列号')
    position: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_general_ci'), comment='设备安装位置，如大门，1号巷道口等')
    is_stop: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    update_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(tz_utc_8))


class CardsTable(Base):
    __tablename__ = 'cards_table'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, comment='卡号id')
    card_id: Mapped[str] = mapped_column(String(255, 'utf8mb4_general_ci'), comment='卡号')
    worker_id: Mapped[Optional[int]] = mapped_column(Integer, comment='该卡对应的工人')
    hat_id: Mapped[Optional[int]] = mapped_column(Integer, comment='该卡对应的头盔id')
    is_stop: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='停用')
    update_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(tz_utc_8))


class HatsTable(Base):
    __tablename__ = 'hats_table'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    hat_color: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_general_ci'), comment='头盔颜色')
    hat_functions: Mapped[Optional[str]] = mapped_column(String(255, 'utf8mb4_general_ci'), comment='头盔功能，如有无摄像头，获取哪些数据等')
    is_stop: Mapped[Optional[int]] = mapped_column(TINYINT(1))
    update_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(tz_utc_8))


class WorkersLoginTable(Base):
    __tablename__ = 'workers_login_table'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, comment='记录id')
    card_id: Mapped[int] = mapped_column(Integer, comment='对应的卡号')
    device_id: Mapped[int] = mapped_column(Integer, comment='读取此事件的设备')
    worker_id: Mapped[Optional[int]] = mapped_column(Integer, comment='对应的工人')
    update_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(tz_utc_8))


class WorkersTable(Base):
    __tablename__ = 'workers_table'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, comment='工人ID')
    name: Mapped[str] = mapped_column(String(255, 'utf8mb4_general_ci'))
    gender: Mapped[int] = mapped_column(TINYINT(1), comment='性别1男0女')
    birthday: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='出生日期')
    is_stop: Mapped[Optional[int]] = mapped_column(TINYINT(1), comment='为1停用')
    update_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='状态更新时间')
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, comment='入职时间', default=lambda: datetime.datetime.now(tz_utc_8))


class AIQATable(Base):
    __tablename__ = 'AI_worker_question_table'

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    url: Mapped[str] = mapped_column(String(255, 'utf8mb4_general_ci'))
    question: Mapped[str] = mapped_column(String(255, 'utf8mb4_general_ci'))
    answer: Mapped[str] = mapped_column(String(255, 'utf8mb4_general_ci'))
    update_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(tz_utc_8))
