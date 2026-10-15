from fastapi import APIRouter, Request
from starlette import status
from database.core import database_dependency
from auth.service import user_dependency
from .schemas import CultivationRequest, RoleRequest, AudiLogResponse, AllDeviceResponse, DeviceInformationResponse, TelemetryDataResponse, DeviceApiKeyResponse
from .service import *
from typing import Optional

router = APIRouter()

@router.get("/all-users", status_code = status.HTTP_200_OK)
async def all_users(db : database_dependency, user : user_dependency, request : Request):
    return await get_all_users(db, user)

@router.get("/user-information/", status_code = status.HTTP_200_OK)
async def all_users(db : database_dependency, user : user_dependency, request : Request, public_id : Optional[str] = None, username : Optional[str] = None, email : Optional[str] = None):
    return await get_user(public_id, username, email, db, user)

@router.put("/change-user-status/{public_id}", status_code = status.HTTP_204_NO_CONTENT)
async def change_user_status(public_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await update_user_status(public_id, db, user)
    
@router.put("/change-user-role/{public_id}", status_code = status.HTTP_204_NO_CONTENT)
async def change_user_role(public_id : str, new_role : RoleRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_user_role(public_id, new_role, db, user)

@router.put("/reset-user-password/{public_id}", status_code = status.HTTP_200_OK)
async def reset_user_password(public_id : str, db : database_dependency, user : user_dependency):
    return await reset_password_by_admin(public_id, db , user)

@router.delete("/delete-user/{public_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(public_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await delete_account(db, user, public_id)

@router.get("/audit-logs", response_model = list[AudiLogResponse])
async def audit_logs(db : database_dependency, user : user_dependency, request : Request, user_id_for_logs : Optional[str] = None, device_public_id : Optional[str] = None):
    return await get_audit_logs(user_id_for_logs, device_public_id, db, user)

@router.get("/show-typ-of-cultivation", status_code = status.HTTP_200_OK)
async def new_cultivation(db : database_dependency, user : user_dependency, request : Request, cultivation_type : Optional[str] = None):
    return await get_cultivations(cultivation_type, db, user)

@router.post("/add-new-cultivation-type", status_code = status.HTTP_201_CREATED)
async def new_cultivation(cultivation_request : CultivationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await add_new_cultivation(cultivation_request, db, user)

@router.put("/change-cultivation-type/{type_of_cultivation}", status_code = status.HTTP_204_NO_CONTENT)
async def new_cultivation(type_of_cultivation : str, cultivation_request : CultivationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_cultivation(type_of_cultivation, cultivation_request, db, user)

@router.put("/delete-cultivation-type/{type_of_cultivation}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_cultivation(type_of_cultivation : str, db : database_dependency, user : user_dependency, request : Request):
    return await delete_cult_type(type_of_cultivation, db, user)

@router.get("/get-all-register-device", response_model = list[AllDeviceResponse], status_code = status.HTTP_200_OK)
async def get_all_register_device(db : database_dependency, user : user_dependency, request : Request):
    return await get_all_device(db, user)

@router.get("/get-all-register-user-device/{public_id}", response_model = list[AllDeviceResponse], status_code = status.HTTP_200_OK)
async def get_all_register_user_device(public_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await get_all_user_devices(public_id, db, user)

@router.get("/get-device-information/{public_device_id}", response_model = list[DeviceInformationResponse], status_code = status.HTTP_200_OK)
async def get_device_information(public_device_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await show_device_information(public_device_id, db, user)

@router.delete("/delete-register-device/{public_device_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_register_device(public_device_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await delete_device(public_device_id, db, user)

@router.get("/check-device-telemetry-data-logs/{public_device_id}", response_model = list[TelemetryDataResponse], status_code = status.HTTP_200_OK)
async def check_device_telemetry_data_logs(public_device_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await check_device_data_logs(public_device_id, db, user)

@router.get("/get-all-device-tokens/{public_device_id}", response_model = list[DeviceApiKeyResponse], status_code = status.HTTP_200_OK)
async def get_all_device_tokens(public_device_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await get_device_tokens(public_device_id, db, user)

@router.put("/change-status-of-device-communication-token/{public_device_id}", status_code = status.HTTP_204_NO_CONTENT)
async def change_status_of_device_communication_token(public_device_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await change_token_status(public_device_id, db, user)