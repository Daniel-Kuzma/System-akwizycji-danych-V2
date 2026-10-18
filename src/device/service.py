from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy import select, update, desc, delete
from database.models import Device, DeviceApiKey, TypyOfCultivation, CultivationAnalysis
from core.admin_logger import create_audit_log
from auth.service import crypt_context
from .schemas import DeviceNameRequest, ChangeDeviceInformationRequest, DeviceRequest
import secrets
from datetime import datetime

async def user_check(user):
    if user.get("role") != "user":
        HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "You do not have access to this page")
    pass

async def device_public_id_check(device_public_id : str, db : AsyncSession):
    device_stmt = await db.execute(select(Device).where(Device.public_id == device_public_id).limit(1))
    device_result = device_stmt.scalar()
    if not device_result:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Device with this public id dose not exist")
    return device_result

async def all_account_device(db : AsyncSession, user):
    await user_check(user)
    try:
        device_stmt = await db.execute(select(*Device.__table__.c, TypyOfCultivation.name_of_cultivation)
                                       .join(TypyOfCultivation, Device.type_of_cultivation_id == TypyOfCultivation.id)
                                       .where(Device.owner_id == user.get("private_id")))
        device_result = device_stmt.mappings().all()
        return device_result
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Critical problem with server {e}")
    
async def user_specify_device(public_device_ip, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    try:
        device_stmt = await db.execute(select(*Device.__table__.c, TypyOfCultivation.name_of_cultivation)
                                       .join(TypyOfCultivation, Device.type_of_cultivation_id == TypyOfCultivation.id)
                                       .where(Device.id == device_result.id).limit(1))
        device_output_result = device_stmt.mappings().all()
        return device_output_result
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Critical problem with server {e}")

async def create_device(user_request : DeviceRequest, db : AsyncSession, user):
    await user_check(user)
    try:
        new_device = Device(owner_id = user.get("private_id"),
                            type_of_cultivation_id = user_request.type_of_cultivation,
                            device_name = user_request.device_name,
                            device_location = user_request.device_location,
                            is_email_alert_enable = user_request.is_email_alert_enable)
        db.add(new_device)
        await db.flush()
        token = f"{new_device.public_id}." + secrets.token_hex(8)
        device_token = DeviceApiKey(device_id = new_device.id,
                                    token = crypt_context.hash(token))
        db.add(device_token)
        await db.flush()
        await create_audit_log(db, user_id = user.get("private_id"), action = "CREATE NEW DEVICE", entity_type = "devices", entity_id = str(new_device.public_id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "CREATE NEW DEVICE TOKEN", entity_type = "device_api_keys", entity_id = str(new_device.public_id))
        await db.commit()
        return {"message" : "Successfully created device"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Critical problem with server {e}")

async def update_device_information(user_request : ChangeDeviceInformationRequest, public_device_ip, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    try:
        await db.execute(update(Device).values(type_of_cultivation_id = user_request.type_of_cultivation,
                                               device_name = user_request.device_name,
                                               device_location = user_request.device_location,
                                               is_email_alert_enable = user_request.is_email_alert_enable)
                                               .where(Device.id == device_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE DEVICE", entity_type = "devices", entity_id = str(device_result.public_id))
        await db.commit()
        return {"message" : "Successfully updated device information"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Critical problem with server {e}")

async def create_new_cultivation_analysis_by_user(device_public_id : str, db : AsyncSession, user):
    user_check(user)
    device_result = await device_public_id_check(device_public_id, db)
    stmt = await db.execute(select(CultivationAnalysis.id)
                            .where(CultivationAnalysis.device_id == device_result.id)
                            .where(CultivationAnalysis.analysis_end_date.is_(None)))
    result = stmt.scalar()
    if result is not None:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "If you want to start new analize you need to end last cultivation analysis")
    try:
        new_analize = CultivationAnalysis(
            device_id = device_result.id,
            type_of_cultivation_id = device_result.type_of_cultivation_id,
        )
        db.add(new_analize)
        await db.commit()
        return {"message" : "Start new cultivation analysis"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def stop_cultivation_analysis_by_user(device_public_id : str, db : AsyncSession, user):
    user_check(user)
    device_result = await device_public_id_check(device_public_id, db)
    stmt = await db.execute(select(CultivationAnalysis)
                            .where(CultivationAnalysis.device_id == device_result.id)
                            .order_by(desc(CultivationAnalysis.analysis_start_date))
                            .limit(1))
    result = stmt.scalar()
    if result is None:
        return None

    if result.analysis_end_date:
        return None
    
    try:
        await db.execute(update(CultivationAnalysis)
                         .values(analysis_end_date = datetime.now())
                         .where(CultivationAnalysis.id == result.id))
        await db.commit()
        return {"message" : "Successfully end cultivation analysis"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

# zmian na tworzenie nowego a nie update 
async def update_device_key(public_device_ip, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    try:
        token = f"{device_result.public_id}." + secrets.token_hex(8)
        await db.execute(update(DeviceApiKey).values(token = crypt_context.hash(token)).where(DeviceApiKey.device_id == device_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE DEVICE TOKEN", entity_type = "device_api_keys", entity_id = str(device_result.public_id))
        await db.commit()
        return {"message" : f"Successfully updated device token : {token}"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Critical problem with server {e}")

async def change_token_activity(public_device_ip, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    token_activity_stm = await db.execute(select(DeviceApiKey.is_active).where(DeviceApiKey.id == device_result.id).order_by(desc(DeviceApiKey.created_at)).limit(1))
    token_activity_result = token_activity_stm.scalar()
    new_token_activity = True if token_activity_result is False else False
    try:
        await db.execute(update(DeviceApiKey).values(is_active = new_token_activity).where(DeviceApiKey.device_id == device_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE DEVICE TOKEN ACTIVITY", entity_type = "device_api_keys", entity_id = str(device_result.public_id))
        await db.commit()
        return {"message" : "Successfully updated device token activity"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Critical problem with server {e}")

async def delete_device_by_user(public_device_ip : str, user_request : DeviceNameRequest, db : AsyncSession, user):
    await user_check(user)
    device_result = await device_public_id_check(public_device_ip, db)
    if user_request.device_name != device_result.device_name:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Provides the correct name of device")
    try:
        await create_audit_log(db, user_id = user.get("private_id"), action = "DELETE DEVICE", entity_type = "devices", entity_id = str(device_result.public_id))
        await db.execute(delete(Device).where(Device.id == device_result.id))
        await db.commit()
        return {"message" : "Successfully delete device"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Critical problem with server {e}")