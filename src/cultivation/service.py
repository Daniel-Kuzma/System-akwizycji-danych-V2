from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import TypyOfCultivation
from fastapi import HTTPException
from starlette import status
from core.server_logger import logger

async def get_cultivation(db : AsyncSession):
    try:
        cultivation_stmt = await db.execute(select(TypyOfCultivation))
        cultivation_result = cultivation_stmt.scalars()
        return [] if cultivation_result is None else cultivation_result
    except Exception as e:
        await logger.exception("Critical problem with server")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server")