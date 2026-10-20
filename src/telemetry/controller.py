from fastapi import APIRouter, Request
from database.core import database_dependency
from auth.service import user_dependency
from typing import Optional
from starlette import status
from .service import get_telemeter_based_on_time, analyze_the_temperature_result, analyze_the_humidity_result
from .schemas import TelemeterRespond, AnalizeRespons
from core.limiter import limiter
import uuid

router = APIRouter()

@router.get("/get-data-based-on-selected-time-period/{device_public_id}", response_model = list[TelemeterRespond] , status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def get_data_based_on_selected_time_period(device_public_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request, time : Optional[str] = None):
    return await get_telemeter_based_on_time(device_public_id, time, db, user)

@router.get("/get-cultivation-temperature-analyses/{device_public_id}", response_model = AnalizeRespons, status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def get_cultivation_temperature_analyses(device_public_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await analyze_the_temperature_result(device_public_id, db, user)

@router.get("/get-cultivation-humidity-analyses/{device_public_id}", response_model = AnalizeRespons, status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def get_cultivation_humidity_analyses(device_public_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await analyze_the_humidity_result(device_public_id, db, user)