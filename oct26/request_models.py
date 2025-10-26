from pydantic import BaseModel, PositiveInt
from datetime import datetime


class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None
    tastes: dict[str, PositiveInt]


