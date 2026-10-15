from pydantic import BaseModel, Field
from enum import Enum
from datetime import timedelta


class TimeEnum(str, Enum):
    LAST_HOUR = "LAST_HOUR"
    LAST_HALF_DAY = "LAST_HALF_DAY"
    LAST_DAY = "LAST_DAY"
    LAST_WEEK = "LAST_WEEK"
    LAST_15_DAYS = "LAST_15_DAYS"
    LAST_MONTH = "LAST_MONTH"
    LAST_90_DAYS = "LAST_90_DAYS"

class TimeRequest(BaseModel):
    time : TimeEnum