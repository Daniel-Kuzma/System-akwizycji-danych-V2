from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, AuditLog, TypyOfCultivation
from sqlalchemy import select, update
from sqlalchemy.orm import defer
from fastapi import HTTPException
from starlette import status
from schemas import CultivationRequest
from core.admin_logger import create_audit_log

async def get_all_users(db : AsyncSession, user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")
    try:
        stmt = await db.execute(select(User).options(defer(User.id), defer(User.password)))
        stmt_result = stmt.scalars().all()
        return stmt_result
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def get_user(public_id : str, db : AsyncSession, user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")
    stmt = await db.execute(select(User).where(User.public_id == public_id).options(defer(User.id), defer(User.password)))
    stmt_result = stmt.scalar()
    if stmt_result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "User with this public id dose not exist")
    try:
        return stmt_result
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def update_user_status(public_id : str, new_status : bool, db : AsyncSession, user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")
    
    user_stmt = await db.execute(select(User).where(User.public_id == public_id).limit(1))
    user_result = user_stmt.scalar()
    if user_result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "User with this public id dose not exist")

    try:
        await db.execute(update(User).values(is_active = new_status).where(User.id == user_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE USER STATUS", entity_type = "user", entity_id = user_result.public_id)
        await db.commit()
        return {"detail" : "Successfully changed user status"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server ")


async def update_user_role(public_id : str, new_role : str, db : AsyncSession, user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")
    
    user_stmt = await db.execute(select(User).where(User.public_id == public_id).limit(1))
    user_result = user_stmt.scalar()
    if user_result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "User with this public id dose not exist")

    try:
        await db.execute(update(User).values(user_role = new_role).where(User.id == user_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE ROLE", entity_type = user, entity_id = user_result.public_id)
        await db.commit()
        return {"detail" : "Successfully changed user role"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")


async def delete(public_id : str, db : AsyncSession, user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")
    
    user_stmt = await db.execute(select(User).where(User.public_id == public_id).limit(1))
    user_result = user_stmt.scalar()
    if user_result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "User with this public id dose not exist")

    try:
        await db.execute(delete(User).where(User.id == user_result.id))
        await create_audit_log(db, user_id = user.get("private_id"), action = "DELETE USER", entity_type = "user", entity_id = user_result.public_id)
        await db.commit()
        return {"detail" : "Successfully deleted user"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def get_audit_logs(user_id_for_logs, db : AsyncSession, user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")
    
    if user_id_for_logs:
        is_user_exist_stm = await db.execute(select(User).where(User.public_id == user_id_for_logs).limit(1))
        is_user_exist_result = is_user_exist_stm.scalar()
        if is_user_exist_result is None:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "User with this public id dose not exist")
    
    try:
        if user_id_for_logs is None:
            logs_stmt = await db.execute(select(AuditLog))
            logs_result = logs_stmt.scalars().all()
            return logs_result
        else:
            logs_for_user_stmt = await db.execute(select(AuditLog).where(AuditLog.user_id == is_user_exist_result.id))
            logs_for_user_result = logs_for_user_stmt.scalars.all()
            return logs_for_user_result
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def get_cultivations(cultivation_type, db : AsyncSession, user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")
    if cultivation_type:
        is_cultivation_exist_stmt = await db.execute(select(TypyOfCultivation).where(TypyOfCultivation.name_of_cultivation == cultivation_type).limit(1))
        is_cultivation_exist_result = is_cultivation_exist_stmt.scalar()
        if is_cultivation_exist_result is None:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "This cultivation dose not exist")
    try:
        if cultivation_type is None:
            all_cultivation_stmt = await db.execute(select(TypyOfCultivation))
            all_cultivation_result = all_cultivation_stmt.scalars().all()
            return all_cultivation_result
        else:
            return is_cultivation_exist_result
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def add_new_cultivation(cultivation_request : CultivationRequest, db : AsyncSession, user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")

    try:
        new_cultivation = TypyOfCultivation(name_of_cultivation = cultivation_request.name_of_cultivation,
                                            min_temperature = cultivation_request.min_temperature,
                                            max_temperature = cultivation_request.max_temperature,
                                            min_humidity = cultivation_request.min_humidity,
                                            max_humidity = cultivation_request.max_humidity)
        db.add(new_cultivation)
        await db.flush()
        await create_audit_log(db, user_id = user.get("private_id"), action = "CREATE CULTIVATION", entity_type = "type_of_cultivation", entity_id = new_cultivation.id)

        await db.commit()
        return {"detail" : "Successfully added new cultivation type"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def update_cultivation(type_of_cultivation, cultivation_request : CultivationRequest, db : AsyncSession, user):
    if user.get("role") != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")

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
        await db.commit()
        return {"detail" : "Successfully updated cultivation"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def delete_cult_type(type_of_cultivation, db : AsyncSession, user):
    if user.get("role") != "admin":
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You have no access to this page")
    
    is_cultivation_exist_stmt = await db.execute(select(TypyOfCultivation).where(TypyOfCultivation.name_of_cultivation == type_of_cultivation).limit(1))
    is_cultivation_exist_result = is_cultivation_exist_stmt.scalar()
    if is_cultivation_exist_result is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "This cultivation dose not exist")

    try:
        await db.execute(delete(TypyOfCultivation).where(TypyOfCultivation.name_of_cultivation == type_of_cultivation))
        await db.commit()
        return {"detail" : "Successfully deleted cultivation"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")