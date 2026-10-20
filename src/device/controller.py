from fastapi import APIRouter, Request
from starlette import status
from database.core import database_dependency
from auth.service import user_dependency
from .schemas import DeviceNameRequest, DeviceRequest, ChangeDeviceInformationRequest, AllUserDeviceResponse, USerDeviceResponse, SuccessfulRespond, SuccessfulRespondToken
from .service import *
from core.limiter import limiter
import uuid
router = APIRouter()

@router.get("/all-user-device", response_model = list[AllUserDeviceResponse], status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def all_user_device(db : database_dependency, user : user_dependency, request : Request):
    return await all_account_device(db, user)

@router.get("/user-device/{public_device_id}", response_model = USerDeviceResponse, status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def user_device(public_device_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await user_specify_device(public_device_id, db, user)

@router.post("/create-new-device", response_model = SuccessfulRespond, status_code = status.HTTP_201_CREATED)
@limiter.limit("50/minute")
async def create_new_device(user_request : DeviceRequest, db : database_dependency, user : user_dependency, request : Request):
    return await create_device(user_request, db, user)

@router.put("/change-device-information/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def change_device_information(public_device_id : uuid.UUID, user_request : ChangeDeviceInformationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_device_information(user_request, public_device_id, db, user)

@router.post("/start-new-cultivation-analysis-by-user/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_201_CREATED)
@limiter.limit("50/minute")
async def start_new_cultivation_analysis_by_user(public_device_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await create_new_cultivation_analysis_by_user(public_device_id, db, user)

@router.put("/end-cultivation-analysis-by-user/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def end_cultivation_analysis_by_user(public_device_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await stop_cultivation_analysis_by_user(public_device_id, db, user)

@router.put("/generate-new-key-for-device/{public_device_id}", response_model = SuccessfulRespondToken, status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def generate_new_key_for_device(public_device_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await update_device_key(public_device_id, db, user)

@router.put("/change-device-token-activity/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def change_device_token_activity(public_device_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await change_token_activity(public_device_id, db, user)

@router.delete("/delete-device/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def delete_device(public_device_id : uuid.UUID, user_request : DeviceNameRequest, db : database_dependency, user : user_dependency, request : Request):
    return await delete_device_by_user(public_device_id, user_request, db, user)