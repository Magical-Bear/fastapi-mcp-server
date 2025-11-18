from pydantic import BaseModel


class LightControlModel(BaseModel):
    light_id: str
    status: bool
