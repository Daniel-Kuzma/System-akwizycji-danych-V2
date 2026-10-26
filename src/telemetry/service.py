from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Device, TelemetryData, DeviceApiKey, TypyOfCultivation, CultivationAnalysis, User
from sqlalchemy import select, desc, func
from auth.service import crypt_context
from datetime import datetime
from fastapi import HTTPException
from starlette import status
from database.models import TelemetryData
from datetime import timedelta
import uuid
from core.server_logger import logger
from core.email_sender import send_email

TIME_MAPPING = {
    "LAST_HOUR" : timedelta(hours=1),
    "LAST_HALF_DAY" : timedelta(hours=12),
    "LAST_DAY" : timedelta(days=1),
    "LAST_WEEK" : timedelta(weeks=1),
    "LAST_15_DAYS" : timedelta(days=15),
    "LAST_MONTH" : timedelta(days=30),
    "LAST_90_DAYS" : timedelta(days=90)
}

async def check_user(user):
    if user.get("role") != "user":
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "You do not have access to this page")

async def device_check(device_public_id : str, db : AsyncSession):
    stmt = await db.execute(select(Device).where(Device.public_id == device_public_id).limit(1))
    result = stmt.scalar()
    if not result:
        return False
    return result

async def token_verification(key_token : str, device_id : int,  db : AsyncSession):
    stmt = await db.execute(select(DeviceApiKey.token)
                            .where(DeviceApiKey.device_id == device_id, DeviceApiKey.is_active == True)
                            .order_by(desc(DeviceApiKey.created_at))
                            .limit(1))
    result = stmt.scalar()
    if not result:
        return False

    if not crypt_context.verify(key_token, result):
        return False
    
    return True

async def send_email_if_conditions_are_critical(device_id, temperature : float, humidity : float, db : AsyncSession):
    stmt = await db.execute(select(Device).where(Device.id == device_id).limit(1))
    result = stmt.scalar()
    if result.is_email_alert_enable:
        cultivation_stmt = await db.execute(select(TypyOfCultivation).where(TypyOfCultivation.id == result.type_of_cultivation_id).limit(1))
        cultivation_result = cultivation_stmt.scalar()
        user_email_stmt = await db.execute(select(User.email).where(User.id == result.owner_id).limit(1))
        user_email_result = user_email_stmt.scalar()
        if cultivation_result.max_temperature < temperature or cultivation_result.min_temperature > temperature:
            await send_email(user_email_result, "Poor temperature conditions", f"{result.device_name} in the {result.device_location} recorded unfavorable temperature conditions: {temperature} °C")
        if cultivation_result.max_humidity < humidity or cultivation_result.min_humidity > humidity:
            await send_email(user_email_result, "Poor humidity conditions", f"{result.device_name} in the {result.device_location} recorded unfavorable humidity conditions: {humidity} %")


async def save_telemeter_in_database(token : str, temperature : float, humidity : float, db : AsyncSession):
    verification_token = token.split(".")
    device_result = await device_check(verification_token[0], db)
    device_id = device_result.id
    if not device_id:
        return False
    if await token_verification(token, device_id, db):
        send_email_if_conditions_are_critical(device_id, temperature, humidity, db)
        try: 
            new_telemetry = TelemetryData(device_id = device_id, temperature_reading = temperature, humidity_reading = humidity)
            db.add(new_telemetry)
            await db.commit()
            return f"Added data for device: {verification_token[0]}, "
        except Exception as e:
            await db.rollback()
            logger.exception("Problem with saving telemetry data from esp32")
    return False

async def get_telemeter_based_on_time(public_device_id : uuid.UUID, time : str, db : AsyncSession, user):
    await check_user(user)
    device_result = await device_check(public_device_id, db)
    if not device_result:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "This device does not exist")
    try:
        if time is None:
            stmt = await db.execute(select(TelemetryData).where(TelemetryData.device_id == device_result.id))
            return stmt.scalars().all()
        data_flag = datetime.now() - TIME_MAPPING[time]
        stmt = await db.execute(select(TelemetryData).where(TelemetryData.device_id == device_result.id).where(TelemetryData.created_at >= data_flag))
        return stmt.scalars().all()
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")

async def analyze_the_temperature_result(public_device_id : uuid.UUID, db : AsyncSession, user):
    await check_user(user)
    device_result = await device_check(public_device_id, db)
    if not device_result:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "This device does not exist")
    try:
        cultivation_stmt = await db.execute(select(*CultivationAnalysis.__table__.c, *TypyOfCultivation.__table__.c)
                                            .join(TypyOfCultivation, CultivationAnalysis.type_of_cultivation_id == TypyOfCultivation.id)
                                            .where(CultivationAnalysis.device_id == device_result.id)
                                            .order_by(desc(CultivationAnalysis.analysis_start_date)))
        cultivation_result = cultivation_stmt.mappings().all()
        if not cultivation_result:
            return {"percentage": 0.0}
        end_date_flag = datetime.now() if cultivation_result[0]["analysis_end_date"] == None else cultivation_result[0]["analysis_end_date"]
        stmt = await db.execute(select(func.count()).select_from(TelemetryData)
                                .where(TelemetryData.device_id == device_result.id)
                                .where(TelemetryData.temperature_reading >= cultivation_result[0]["min_temperature"])
                                .where(TelemetryData.temperature_reading <= cultivation_result[0]["max_temperature"])
                                .where(TelemetryData.created_at >= cultivation_result[0]["analysis_start_date"])
                                .where(TelemetryData.created_at <= end_date_flag))
        result_of_good_data = stmt.scalar()
        count_stmt = await db.execute(select(func.count()).select_from(TelemetryData)
                                .where(TelemetryData.device_id == device_result.id)
                                .where(TelemetryData.created_at >= cultivation_result[0]["analysis_start_date"])
                                .where(TelemetryData.created_at <= end_date_flag))
        result_of_all_data = count_stmt.scalar()

        if result_of_all_data == 0:
            return {"percentage": 0.0}

        percentage_result = round(result_of_good_data/result_of_all_data*100,1)
        return {"percentage" : percentage_result}
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")    

async def analyze_the_humidity_result(public_device_id : uuid.UUID, db : AsyncSession, user):
    await check_user(user)
    device_result = await device_check(public_device_id, db)
    if not device_result:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "This device does not exist")
    try:
        cultivation_stmt = await db.execute(select(*CultivationAnalysis.__table__.c, *TypyOfCultivation.__table__.c)
                                            .join(TypyOfCultivation, CultivationAnalysis.type_of_cultivation_id == TypyOfCultivation.id)
                                            .where(CultivationAnalysis.device_id == device_result.id)
                                            .order_by(desc(CultivationAnalysis.analysis_start_date)))
        cultivation_result = cultivation_stmt.mappings().all()
        if not cultivation_result:
            return {"percentage": 0.0}
        end_date_flag = datetime.now() if cultivation_result[0]["analysis_end_date"] == None else cultivation_result[0]["analysis_end_date"]
        stmt = await db.execute(select(func.count()).select_from(TelemetryData)
                                .where(TelemetryData.device_id == device_result.id)
                                .where(TelemetryData.humidity_reading >= cultivation_result[0]["min_humidity"])
                                .where(TelemetryData.humidity_reading <= cultivation_result[0]["max_humidity"])
                                .where(TelemetryData.created_at >= cultivation_result[0]["analysis_start_date"])
                                .where(TelemetryData.created_at <= end_date_flag))
        result_of_good_data = stmt.scalar()
        count_stmt = await db.execute(select(func.count()).select_from(TelemetryData)
                                .where(TelemetryData.device_id == device_result.id)
                                .where(TelemetryData.created_at >= cultivation_result[0]["analysis_start_date"])
                                .where(TelemetryData.created_at <= end_date_flag))
        result_of_all_data = count_stmt.scalar()

        if result_of_all_data == 0:
            return {"percentage": 0.0}

        percentage_result = round(result_of_good_data/result_of_all_data*100,1)
        return {"percentage" : percentage_result}
    except Exception as e:
        logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")    

    
    