from datetime import date, datetime
from typing import List
from pydantic import BaseModel, Field


class DateModel(BaseModel):
    date_list: List[date] = Field(..., description="输入datetime日期对象列表")


class PositionModel(BaseModel):
    day: date = Field(..., description="输入指定日期，格式为datetime日期对象")
    position: str = Field(..., description="查询的区域名称，名称有1号巷道 2号巷道 3号巷道 1号竖井 2号竖井 1号平导 厂区大门")