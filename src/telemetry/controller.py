from fastapi import APIRouter, Request
from database.core import database_dependency
from auth.service import user_dependency
from typing import Optional
from .schemas import TimeRequest
from starlette import status
from .service import get_telemeter_based_on_time

router = APIRouter()

@router.get("/get-data-based-on-selected-time-period/{device_public_id}", status_code = status.HTTP_200_OK)
async def get_data_based_on_selected_time_period(device_public_id : str, db : database_dependency, user : user_dependency, request : Request, time : Optional[TimeRequest] = None):
    return await get_telemeter_based_on_time(device_public_id, time, db, user)
    