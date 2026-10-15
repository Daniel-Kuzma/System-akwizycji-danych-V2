from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Device, TelemetryData, DeviceApiKey
from sqlalchemy import select, desc
from auth.service import crypt_context

async def device_check(device_public_id : str, db : AsyncSession):
    stmt = await db.execute(select(Device.id).where(Device.public_id == device_public_id).limit(1))
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
    device_id = await device_check(verification_token[0], db)
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

    
