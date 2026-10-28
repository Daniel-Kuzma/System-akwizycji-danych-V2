from pydantic import BaseModel, ConfigDict

class CultivationRespond(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : int
    name_of_cultivation : str

class CultivationExpendedRespons(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name_of_cultivation : str
    min_temperature : float
    max_temperature : float
    min_humidity : float
    max_humidity : float


