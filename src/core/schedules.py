from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.models import Device, TelemetryData
from datetime import datetime, timedelta
from starlette import status


async def change_device_status(db: AsyncSession):
    time_flag = datetime.now() - timedelta(minutes=10)
    try:
        active_devices_subq = (
            select(TelemetryData.device_id)
            .where(TelemetryData.created_at > time_flag)
            .distinct()
        )

        stmt = (
            update(Device)
            .where(Device.id.not_in(active_devices_subq))
            .where(Device.device_status != "OFFLINE") 
            .values(device_status="OFFLINE")
        )
        
        await db.execute(stmt)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")
