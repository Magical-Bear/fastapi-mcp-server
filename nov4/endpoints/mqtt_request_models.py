from pydantic import BaseModel


class SensorDataModel(BaseModel):
    temperature: float
    humidity: float
