from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy import select, update
from database.models import Device, DeviceApiKey
from core.admin_logger import create_audit_log
from auth.service import crypt_context
from schemas import DeviceNameRequest, ChangeDeviceInformationRequest, DeviceRequest
import secrets

async def user_check(user):
    if user.get("role") != "user":
        HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "You have not access to this page")
    pass

async def device_public_id_check(device_public_id : str, db : AsyncSession):
    device_stmt = await db.execute(select(Device).where(Device.public_id == device_public_id).limit(1))
    device_result = device_stmt.scalar()
    if not device_result:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Device with this public id dose not exist")
    return device_result

async def all_user_device(db : AsyncSession, user):
    await user_check(user)
    try:
        device_stmt = await db.execute(select(Device.device_name, Device.device_location, Device.type_of_cultivation_id)
                                       .where(Device.owner_id == user.get("private_id")))
        device_result = device_stmt.scalars().all()
        if not device_result:
            return {"detail" : "You did not add any device"}
        return device_result
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server ")
    
async def user_specify_device(public_device_ip, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    try:
        return device_result
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server ")

async def create_device(user_request : DeviceRequest, db : AsyncSession, user):
    await user_check(user)
    try:
        new_device = Device(owner_id = user.get("private_id"),
                            type_of_cultivation_id = user_request.type_of_cultivation,
                            device_name = user_request.device_name,
                            device_location = user_request.device_location)
        db.add(new_device)
        await db.flush()
        token = f"{new_device.public_id}." + secrets.token_hex(8)
        device_token = DeviceApiKey(device_id = new_device.id,
                                    token = crypt_context.hash(token))
        db.add(device_token)
        await db.flush()
        await create_audit_log(db, user_id = user.get("private_id"), action = "CREATE NEW DEVICE", entity_type = "devices", entity_id = new_device.public_id)
        await create_audit_log(db, user_id = user.get("private_id"), action = "CREATE NEW DEVICE TOKEN", entity_type = "device_api_keys", entity_id = new_device.public_id)
        await db.commit()
        return {"detail" : "Successfully created device"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server ")

async def update_device_information(user_request : ChangeDeviceInformationRequest, public_device_ip, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    try:
        await db.execute(update(Device).values(type_of_cultivation_id = user_request.type_of_cultivation,
                                               device_name = user_request.device_name,
                                               device_location = user_request.device_location)
                                               .where(Device.id == device_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE DEVICE", entity_type = "devices", entity_id = device_result.public_id)
        await db.commit()
        return {"detail" : "Successfully updated device information"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server ")


async def update_device_key(public_device_ip, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    try:
        token = f"{device_result.public_id}." + secrets.token_hex(8)
        await db.execute(update(DeviceApiKey).values(token = crypt_context.hash(token)).where(DeviceApiKey.device_id == device_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE DEVICE TOKEN", entity_type = "device_api_keys", entity_id = device_result.public_id)
        await db.commit()
        return {"detail" : "Successfully updated device token"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server ")

async def change_token_activity(public_device_ip, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    token_activity_stm = await db.execute(select(DeviceApiKey.is_active).where(DeviceApiKey.id == device_result.id).group_by(DeviceApiKey.created_at.desc()).limit(1))
    token_activity_result = token_activity_stm.scalar()
    new_token_activity = True if token_activity_result is False else False
    try:
        await db.execute(update(DeviceApiKey).values(is_active = new_token_activity).where(DeviceApiKey.device_id == device_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE DEVICE TOKEN ACTIVITY", entity_type = "device_api_keys", entity_id = device_result.public_id)
        await db.commit()
        return {"detail" : "Successfully updated device token activity"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server ")

async def delete(public_device_ip : str, user_request : DeviceNameRequest, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    if user_request.device_name != device_result.device_name:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Provides the correct name of device")
    try:
        await db.execute(delete(Device).where(Device.id == device_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "DELETE DEVICE", entity_type = "devices", entity_id = device_result.public_id)
        await db.commit()
        return {"detail" : "Successfully delete device"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server ")

