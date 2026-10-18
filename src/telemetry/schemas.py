from pydantic import BaseModel
from datetime import datetime

class TelemeterRespond(BaseModel):
    temperature_reading : float
    humidity_reading : float
    created_at : datetime

class AnalizeRespons(BaseModel):
    percentage : float
