from fastapi import APIRouter, Request
from starlette import status
from database.core import database_dependency
from auth.service import user_dependency
from .schemas import *
from .service import *
from typing import Optional
from core.limiter import limiter
import uuid
router = APIRouter()

@router.get("/all-users", response_model = list[UserRespons], status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def all_users(db : database_dependency, user : user_dependency, request : Request):
    return await get_all_users(db, user)

@router.get("/user-information", response_model = UserRespons, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def user_information(db : database_dependency, user : user_dependency, request : Request, public_id : Optional[uuid.UUID] = None, username : Optional[str] = None, email : Optional[str] = None):
    return await get_user(public_id, username, email, db, user)

@router.put("/change-user-status/{public_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def change_user_status(public_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await update_user_status(public_id, db, user)
    
@router.put("/change-user-role/{public_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def change_user_role(public_id : uuid.UUID, new_role : RoleRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_user_role(public_id, new_role, db, user)

@router.put("/reset-user-password/{public_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def reset_user_password(public_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await reset_password_by_admin(public_id, db , user)

@router.delete("/delete-user/{public_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def delete_user(public_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await delete_account(public_id, db, user)

@router.get("/audit-logs", response_model = list[AudiLogResponse])
@limiter.limit("100/minute")
async def audit_logs(db : database_dependency, user : user_dependency, request : Request, user_id_for_logs : Optional[uuid.UUID] = None, device_public_id : Optional[uuid.UUID] = None):
    return await get_audit_logs(user_id_for_logs, device_public_id, db, user)

@router.get("/show-all-cultivation", response_model = list[CultivationRespons], status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def get_all_cultivation(db : database_dependency, user : user_dependency, request : Request):
    return await all_cultivations(db, user)

@router.get("/show-information-about-cultivation", response_model = CultivationRespons, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def show_information_about_cultivation(db : database_dependency, user : user_dependency, request : Request, cultivation_type : str):
    return await get_cultivations(cultivation_type, db, user)

@router.post("/add-new-cultivation", response_model = SuccessfulRespond, status_code = status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def new_cultivation(cultivation_request : CultivationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await add_new_cultivation(cultivation_request, db, user)

@router.put("/change-cultivation/{type_of_cultivation}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def change_cultivation(type_of_cultivation : str, cultivation_request : CultivationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_cultivation(type_of_cultivation, cultivation_request, db, user)

@router.delete("/delete-cultivation/{type_of_cultivation}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def delete_cultivation(type_of_cultivation : str, db : database_dependency, user : user_dependency, request : Request):
    return await delete_cult_type(type_of_cultivation, db, user)

@router.get("/get-all-register-device", response_model = list[AllDeviceResponse], status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def get_all_register_device(db : database_dependency, user : user_dependency, request : Request):
    return await get_all_device(db, user)

@router.get("/get-all-register-user-device/{public_id}", response_model = list[AllDeviceResponse], status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def get_all_register_user_device(public_id : uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await get_all_user_devices(public_id, db, user)

@router.get("/get-device-information/{public_device_id}", response_model = list[DeviceInformationResponse], status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def get_device_information(public_device_id: uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await show_device_information(public_device_id, db, user)

@router.put("/change-device-information/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def change_device_information(public_device_id: uuid.UUID, user_request : NewDeviceInformationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_device_information(public_device_id, user_request, db, user)

@router.post("/start-new-cultivation-analysis/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def start_new_cultivation_analysis(public_device_id: uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await create_new_cultivation_analysis(public_device_id, db, user)

@router.put("/end-cultivation-analysis/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def end_cultivation_analysis(public_device_id: uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await stop_cultivation_analysis(public_device_id, db, user)

@router.delete("/delete-register-device/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def delete_register_device(public_device_id: uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await delete_device(public_device_id, db, user)

@router.get("/check-device-telemetry-data-logs/{public_device_id}", response_model = list[TelemetryDataResponse], status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def check_device_telemetry_data_logs(public_device_id: uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await check_device_data_logs(public_device_id, db, user)

@router.get("/get-all-device-tokens/{public_device_id}", response_model = list[DeviceApiKeyResponse], status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def get_all_device_tokens(public_device_id: uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await get_device_tokens(public_device_id, db, user)

@router.put("/change-status-of-device-communication-token/{public_device_id}", response_model = SuccessfulRespond, status_code = status.HTTP_200_OK)
@limiter.limit("100/minute")
async def change_status_of_device_communication_token(public_device_id: uuid.UUID, db : database_dependency, user : user_dependency, request : Request):
    return await change_token_status(public_device_id, db, user)