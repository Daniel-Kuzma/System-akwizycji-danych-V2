from fastapi import APIRouter, Request
from starlette import status
from database.core import database_dependency
from auth.service import user_dependency
from schemas import DeviceNameRequest, DeviceRequest, ChangeDeviceInformationRequest
from service import *

router = APIRouter()

@router.get("/all-user-device", status_code = status.HTTP_200_OK)
async def all_user_device(db : database_dependency, user : user_dependency, request : Request):
    return await user_device(db, user)

@router.get("/user-device/{public_device_ip}", status_code = status.HTTP_200_OK)
async def user_device(public_device_ip : str, db : database_dependency, user : user_dependency, request : Request):
    return await user_specify_device(public_device_ip, db, user)

@router.post("/create-new-device", status_code = status.HTTP_201_CREATED)
async def create_new_device(user_request : DeviceRequest, db : database_dependency, user : user_dependency, request : Request):
    return await create_device(user_request, db, user)

@router.put("/change-device-information/{public_device_ip}", status_code = status.HTTP_204_NO_CONTENT)
async def change_device_information(public_device_ip : str, user_request : ChangeDeviceInformationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_device_information(user_request, public_device_ip, db, user)

@router.put("/generate-new-key-for-device/{public_device_ip}", status_code = status.HTTP_204_NO_CONTENT)
async def change_device_information(public_device_ip : str, db : database_dependency, user : user_dependency, request : Request):
    return await update_device_key(public_device_ip, db, user)

@router.put("/change-device-token-activity/{public_device_ip}", status_code = status.HTTP_204_NO_CONTENT)
async def change_device_token_activity(public_device_ip : str, db : database_dependency, user : user_dependency, request : Request):
    return await change_token_activity(public_device_ip, db, user)

@router.delete("/delete-device/{public_device_ip}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_device(public_device_ip : str, user_request : DeviceNameRequest, db : database_dependency, user : user_dependency, request : Request):
    return await delete(user_request, public_device_ip, db, user)


