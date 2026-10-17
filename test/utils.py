import pytest_asyncio
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from main import app
from fastapi.testclient import TestClient
import pytest
from src.database import models
from src.auth.service import crypt_context, get_current_user
from database import get_db
from datetime import datetime
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def override_get_db():
    async with TestingSessionLocal() as db:
        yield db

def override_get_current_user():
    return {"username": "jan123", "public_id": "07c206d2-3449-451a-9cd7-86a10f6ec18f","private_id" : 1, "role": "admin"}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user 

client = TestClient(app)

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)

