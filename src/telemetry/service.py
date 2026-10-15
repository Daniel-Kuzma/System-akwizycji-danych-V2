from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Device, TelemetryData, DeviceApiKey
from sqlalchemy import select, desc
from auth.service import crypt_context
from datetime import datetime
from fastapi import HTTPException
from starlette import status
from .schemas import TimeRequest
from database.models import TelemetryData
from .schemas import TimeEnum
from datetime import timedelta

TIME_MAPPING = {
    TimeEnum.LAST_HOUR: timedelta(hours=1),
    TimeEnum.LAST_HALF_DAY: timedelta(hours=12),
    TimeEnum.LAST_DAY: timedelta(days=1),
    TimeEnum.LAST_WEEK: timedelta(weeks=1),
    TimeEnum.LAST_15_DAYS: timedelta(days=15),
    TimeEnum.LAST_MONTH: timedelta(days=30),
    TimeEnum.LAST_90_DAYS: timedelta(days=90),
}

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

async def save_telemeter_in_database(token : str, temperature : float, humidity : float, db : AsyncSession):
    verification_token = token.split(".")
    device_result = await device_check(verification_token[0], db)
    device_id = device_result.id
    if not device_id:
        return False
    if await token_verification(token, device_id, db):
        try: 
            new_telemetry = TelemetryData(device_id = device_id, temperature_reading = temperature, humidity_reading = humidity)
            db.add(new_telemetry)
            await db.commit()
            return f"Added data for device: {verification_token[0]}, "
        except Exception as e:
            await db.rollback()
            # dodanie server log z informacją co jest nie tak
            return e
    return False

async def get_telemeter_based_on_time(public_device_id : str, time : TimeRequest, db : AsyncSession, user):
    if user.get("role") != "user":
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "You do not have access to this page")
    device_result = await device_check(public_device_id, db)
    if not device_result:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "This device does not exist")
    try:
        if time is None:
            stmt = await db.execute(select(TelemetryData).where(TelemetryData.device_id == device_result.id))
            return stmt.scalars().all()
        data_flag = datetime.now() - TIME_MAPPING[time.time]
        stmt = await db.execute(select(TelemetryData).where(TelemetryData.device_id == device_result.id).where(TelemetryData.created_at >= data_flag))
        return stmt.scalars().all()
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")
