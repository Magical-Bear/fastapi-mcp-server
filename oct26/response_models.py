from pydantic import BaseModel


class Success(BaseModel):
    status: bool = True
    message: str = "Success"