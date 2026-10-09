from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.settings import settings
from typing import Annotated
from fastapi import Depends

engine = create_async_engine(settings.database_url, connect_args = {"server_settings" : {"timezone" : "Europe/Warsaw"}})
LocalAsyncSession = async_sessionmaker(bind = engine, expire_on_commit = False, autocommit = False)

async def get_db():
    async with LocalAsyncSession() as db:
        yield db

database_dependency = Annotated[AsyncSession, Depends(get_db)]