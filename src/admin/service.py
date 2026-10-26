from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, AuditLog, TypyOfCultivation, Device, DeviceApiKey, TelemetryData, DeviceApiKey, CultivationAnalysis
from sqlalchemy import select, update, delete, desc
from sqlalchemy.orm import defer
from fastapi import HTTPException
from starlette import status
from .schemas import CultivationRequest, RoleRequest, NewDeviceInformationRequest
from core.admin_logger import create_audit_log
from password_generator import PasswordGenerator
from auth.service import crypt_context
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from core.server_logger import logger
from core.email_sender import send_email

async def admin_check(user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You do not have access to this page")
    pass

async def user_check(public_id : str, db : AsyncSession):
    user_stmt = await db.execute(select(User).where(User.public_id == public_id).limit(1))
    user_result = user_stmt.scalar()
    if user_result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "User with this public id dose not exist")
    return user_result

async def device_public_id_check(device_public_id : str, db : AsyncSession):
    device_stmt = await db.execute(select(Device).where(Device.public_id == device_public_id).limit(1))
    device_result = device_stmt.scalar()
    if not device_result:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Device with this public id dose not exist")
    return device_result

async def get_all_users(db : AsyncSession, user):
    await admin_check(user)
    try:
        stmt = await db.execute(select(User))
        stmt_result = stmt.scalars().all()
        return stmt_result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def get_user(public_id : str, username : str, email : str, db : AsyncSession, user):
    await admin_check(user)
    if public_id:
        stmt = await db.execute(select(User)
                                .where(User.public_id == public_id)
                                .options(defer(User.password)))
    elif username:
        stmt = await db.execute(select(User)
                                    .where(User.username == username)
                                    .options(defer(User.password)))
    else:
        stmt = await db.execute(select(User)
                                    .where(User.email == email)
                                    .options(defer(User.password)))

    
    stmt_result = stmt.scalar()
    if stmt_result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "User dose not exist")
    try:
        return stmt_result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def update_user_status(public_id : str, db : AsyncSession, user):
    await admin_check(user)
    user_result = await user_check(public_id, db)
    user_status_stm = await db.execute(select(User.is_active).where(User.id == user_result.id).limit(1))
    user_status_result = user_status_stm.scalar()
    new_status = True if user_status_result is False else False
    try:
        await db.execute(update(User).values(is_active = new_status).where(User.id == user_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE USER STATUS", entity_type = "user", entity_id = str(user_result.public_id))
        await db.commit()
        return {"message" : "Successfully changed user status"}
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Critical problem with server {e}")


async def update_user_role(public_id : str, new_role : RoleRequest, db : AsyncSession, user):
    await admin_check(user)
    user_result = await user_check(public_id, db)
    try:
        await db.execute(update(User).values(user_role = new_role.role).where(User.id == user_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE ROLE", entity_type = "user", entity_id = str(user_result.public_id))
        await db.commit()
        return {"message" : "Successfully changed user role"}
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def reset_password_by_admin(public_id : str, db : AsyncSession, user):
    await admin_check(user)
    user_result = await user_check(public_id, db)
    password_generator = PasswordGenerator()
    random_password = password_generator.generate()
    try:
        await db.execute(update(User).where(User.id == user_result.id).values(password = crypt_context.hash(random_password)))
        await create_audit_log(db, user_id = user.get("private_id"), action = "RESET PASSWORD", entity_type = "user", entity_id = str(user_result.public_id))
        await db.commit()
        await send_email(user_result.email, "New user password", f"This your new password: {random_password}, after login change this password")
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def delete_account(public_id : str, db : AsyncSession, user):
    await admin_check(user)
    user_result = await user_check(public_id, db)
    try:
        await db.execute(delete(User).where(User.id == user_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "DELETE USER", entity_type = "user", entity_id = str(user_result.public_id))
        await db.commit()
        return {"message" : "Successfully deleted user"}
    except Exception as e:
        db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def get_audit_logs(user_id_for_logs, device_public_id, db : AsyncSession, user):
    await admin_check(user)
    if user_id_for_logs:
        user_result = await user_check(user_id_for_logs, db)
    if device_public_id:
        device_result = await device_public_id_check(device_public_id, db)
    try:
        if user_id_for_logs is None and device_public_id is None:
            logs_stmt = await db.execute(select(*AuditLog.__table__.c,
                                                User.public_id)
                                         .join(User, AuditLog.user_id == User.id)
                                         .order_by(AuditLog.created_at.desc()))
            logs_result = logs_stmt.mappings().all()
            return logs_result
        elif device_public_id is None:
            logs_for_user_stmt = await db.execute(select(*AuditLog.__table__.c, User.public_id)
                                                  .join(User, AuditLog.user_id == User.id)
                                                  .where(AuditLog.user_id == user_result.id)
                                                  .order_by(AuditLog.created_at.desc()))
            logs_for_user_result = logs_for_user_stmt.mappings().all()
            return logs_for_user_result
        else:
            device_logs_stmt = await db.execute(select(*AuditLog.__table__.c, User.public_id)
                                                .join(User, AuditLog.user_id == User.id)
                                                .where(AuditLog.entity_id == str(device_result.public_id))
                                                .order_by(AuditLog.created_at.desc()))
            device_logs_result = device_logs_stmt.mappings().all()
            return device_logs_result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def get_cultivations(cultivation_type, db : AsyncSession, user):
    await admin_check(user)
    stmt = await db.execute(select(TypyOfCultivation).where(TypyOfCultivation.name_of_cultivation == cultivation_type).limit(1))
    result = stmt.scalar()
    if result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "This type of cultivation dose not exist")
    try:
        return result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def all_cultivations(db: AsyncSession, user):
    await admin_check(user)
    try:
        stmt = await db.execute(select(TypyOfCultivation))
        result = stmt.scalars().all()
        return result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def add_new_cultivation(cultivation_request : CultivationRequest, db : AsyncSession, user):
    await admin_check(user)

    try:
        new_cultivation = TypyOfCultivation(name_of_cultivation = cultivation_request.name_of_cultivation,
                                            min_temperature = cultivation_request.min_temperature,
                                            max_temperature = cultivation_request.max_temperature,
                                            min_humidity = cultivation_request.min_humidity,
                                            max_humidity = cultivation_request.max_humidity)
        db.add(new_cultivation)
        await db.flush()
        await create_audit_log(db, user_id = user.get("private_id"), action = "CREATE CULTIVATION", entity_type = "type_of_cultivation", entity_id = new_cultivation.name_of_cultivation)
        await db.commit()
        return {"message" : "Successfully added new cultivation type"}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "This cultivation already exist")
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def update_cultivation(type_of_cultivation, cultivation_request : CultivationRequest, db : AsyncSession, user):
    await admin_check(user)

    is_cultivation_exist_stmt = await db.execute(select(TypyOfCultivation).where(TypyOfCultivation.name_of_cultivation == type_of_cultivation).limit(1))
    is_cultivation_exist_result = is_cultivation_exist_stmt.scalar()
    if is_cultivation_exist_result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "This cultivation dose not exist")
    try:
        await db.execute(update(TypyOfCultivation)
                   .values(name_of_cultivation = cultivation_request.name_of_cultivation,
                    min_temperature = cultivation_request.min_temperature,
                    max_temperature = cultivation_request.max_temperature,
                    min_humidity = cultivation_request.min_humidity,
                    max_humidity = cultivation_request.max_humidity)
                    .where(TypyOfCultivation.name_of_cultivation == type_of_cultivation))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE CULTIVATION", entity_type = "types_of_cultivations", entity_id = is_cultivation_exist_result.name_of_cultivation)
        await db.commit()
        return {"message" : "Successfully updated cultivation"}
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def delete_cult_type(type_of_cultivation, db : AsyncSession, user):
    await admin_check(user)
    is_cultivation_exist_stmt = await db.execute(select(TypyOfCultivation).where(TypyOfCultivation.name_of_cultivation == type_of_cultivation).limit(1))
    is_cultivation_exist_result = is_cultivation_exist_stmt.scalar()
    if is_cultivation_exist_result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "This cultivation dose not exist")

    try:
        await db.execute(delete(TypyOfCultivation).where(TypyOfCultivation.name_of_cultivation == type_of_cultivation))
        await create_audit_log(db, user_id = user.get("private_id"), action = "DELETE CULTIVATION", entity_type = "types_of_cultivations", entity_id = is_cultivation_exist_result.name_of_cultivation)
        await db.commit()
        return {"message" : "Successfully deleted cultivation"}
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def get_all_device(db : AsyncSession, user):
    await admin_check(user)
    try:
        device_stmt = await db.execute(select(*Device.__table__.c,
                                              User.public_id.label("owner_public_id"),
                                              TypyOfCultivation.name_of_cultivation)
                                    .join(User, Device.owner_id == User.id)
                                    .join(TypyOfCultivation, Device.type_of_cultivation_id == TypyOfCultivation.id))
        device_result = device_stmt.mappings().all()
        return device_result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def get_all_user_devices(public_id : str, db : AsyncSession, user):
    await admin_check(user)
    user_result = await user_check(public_id, db)
    try:
        device_stmt = await db.execute(select(*Device.__table__.c,
                                              User.public_id.label("owner_public_id"),
                                              TypyOfCultivation.name_of_cultivation)
                                            .join(User, Device.owner_id == User.id)
                                            .join(TypyOfCultivation, Device.type_of_cultivation_id == TypyOfCultivation.id)
                                            .where(Device.owner_id == user_result.id))
        device_result = device_stmt.mappings().all()
        return device_result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def show_device_information(device_public_id : str, db : AsyncSession, user):
    await admin_check(user)
    device_result = await device_public_id_check(device_public_id, db)
    try:
        device_stmt = await db.execute(select(*Device.__table__.c,
                                              User.public_id.label("owner_public_id"),
                                              TypyOfCultivation.name_of_cultivation)
                                            .join(User, Device.owner_id == User.id)
                                            .join(TypyOfCultivation, Device.type_of_cultivation_id == TypyOfCultivation.id)
                                            .where(Device.id == device_result.id))
        device_result = device_stmt.mappings()            
        return device_result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def update_device_information(device_public_id : str, user_request : NewDeviceInformationRequest, db : AsyncSession, user):
    await admin_check(user)
    device_result = await device_public_id_check(device_public_id, db)
    if device_result.type_of_cultivation_id != user_request.type_of_cultivation_id:
        stmt = await db.execute(select(CultivationAnalysis)
                                .where(CultivationAnalysis.device_id == device_result.id)
                                .where(CultivationAnalysis.analysis_end_date.is_(None)))
        result = stmt.scalar()
        if result is not None:
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "If you want to change cultivation type you need to end cultivation analysis")
    try:
        await db.execute(update(Device).values(type_of_cultivation_id = user_request.type_of_cultivation_id,
                                                device_name = user_request.device_name,
                                                device_location = user_request.device_location,
                                                is_email_alert_enable = user_request.is_email_alert_enable)
                                                .where(Device.id == device_result.id))
        await db.commit()
        return {"message" : "Successfully changed device information"}
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def create_new_cultivation_analysis(device_public_id : str, db : AsyncSession, user):
    await admin_check(user)
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
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def stop_cultivation_analysis(device_public_id : str, db : AsyncSession, user):
    await admin_check(user)
    device_result = await device_public_id_check(device_public_id, db)
    stmt = await db.execute(select(CultivationAnalysis)
                            .where(CultivationAnalysis.device_id == device_result.id)
                            .order_by(desc(CultivationAnalysis.analysis_start_date))
                            .limit(1))
    result = stmt.scalar()
    if result is None:
        return {"message" : "There is no active analysis"}

    if result.analysis_end_date:
        return {"message" : "Already end cultivation analyze"}
    
    try:
        await db.execute(update(CultivationAnalysis)
                         .values(analysis_end_date = datetime.now())
                         .where(CultivationAnalysis.id == result.id))
        await db.commit()
        return {"message" : "Successfully end cultivation analysis"}
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Critical problem with server {e}")

async def delete_device(device_public_id : str, db : AsyncSession, user):
    await admin_check(user)
    device_result = await device_public_id_check(device_public_id, db)
    try:
        await db.execute(delete(Device).where(Device.id == device_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "DELETE DEVICE", entity_type = "device", entity_id = str(device_result.public_id))
        await db.commit()
        return {"message" : "Successfully delete device"}
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def check_device_data_logs(device_public_id : str, db : AsyncSession, user):
    await admin_check(user)
    device_result = await device_public_id_check(device_public_id, db)
    try:
        telemetry_logs_stmt = await db.execute(select(*TelemetryData.__table__.c,
                                                       Device.public_id.label("device_public_id"))
                                               .join(Device, TelemetryData.device_id == Device.id)
                                               .where(TelemetryData.device_id == device_result.id)
                                               .order_by(desc(TelemetryData.created_at)))
        telemetry_logs_result = telemetry_logs_stmt.mappings().all()
        return telemetry_logs_result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def get_device_tokens(device_public_id : str, db : AsyncSession, user):
    await admin_check(user)
    device_result = await device_public_id_check(device_public_id, db)
    try:
        device_tokens_stmt = await db.execute(select(*DeviceApiKey.__table__.c,
                                                     Device.public_id.label("device_public_id"))
                                        .join(Device, DeviceApiKey.device_id == Device.id)
                                        .where(DeviceApiKey.device_id == device_result.id)
                                        .order_by(desc(DeviceApiKey.created_at)))
        device_tokens_result = device_tokens_stmt.mappings().all()
        return device_tokens_result
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def change_token_status(device_public_id : str, db : AsyncSession, user):
    await admin_check(user)
    device_result = await device_public_id_check(device_public_id, db)
    token_status_stmt = await db.execute(select(DeviceApiKey)
                                   .where(DeviceApiKey.device_id == device_result.id)
                                   .order_by(desc(DeviceApiKey.created_at)))
    token_status_result = token_status_stmt.scalar()
    new_status = True if token_status_result.is_active is False else False

    try:
        await db.execute(update(DeviceApiKey).values(is_active = new_status).where(DeviceApiKey.id == token_status_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "CHANGE STATUS OF DEVICE TOKEN", entity_type = "device_api_keys", entity_id = str(device_result.public_id))
        await db.commit()
        return {"message" : "Successfully change token status"}
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

