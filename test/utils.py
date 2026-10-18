import pytest_asyncio
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.main import app
from src.database import models
from src.auth.service import crypt_context, get_current_user
from src.database.core import get_db
from fastapi.testclient import TestClient
import pytest
from datetime import datetime, timedelta
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
    return {"username": "jan123", "public_id": "07c206d2-3449-451a-9cd7-86a10f6ec18f", "private_id" : 1, "role": "user"}

def override_get_current_user_v2():
    return {"username": "admin", "public_id": "70f41b40-a522-4ba8-b1cd-ab6a1ca7febd", "private_id" : 2, "role": "admin"}

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

@pytest_asyncio.fixture
async def test_data_users():
    user_1 = models.User(
        id = 1,
        public_id = uuid.UUID("07c206d2-3449-451a-9cd7-86a10f6ec18f"),
        name = "Jan",
        lastname = "Kowalski",
        username = "jan123",
        password = crypt_context.hash("password"),
        email = "jan@gmail.com",
        is_active = True,
        user_role = "user",
        created_at = datetime.now())
    
    user_v2 = models.User(
        id = 2,
        public_id = uuid.UUID("70f41b40-a522-4ba8-b1cd-ab6a1ca7febd"),
        name = "Maciej",
        lastname = "Mazowiecki",
        username = "admin",
        password = crypt_context.hash("password"),
        email = "admin@gmail.com",
        is_active = True,
        user_role = "admin",
        created_at = datetime.now())

    user = [user_1, user_v2]
    
    async with TestingSessionLocal() as db:
        db.add_all(user)
        await db.commit()
        for u in user:
            await db.refresh(u) 
        yield user

@pytest_asyncio.fixture
async def test_data_types_of_cultivations():
    cultivation_1 = models.TypyOfCultivation(
        id = 1,
        name_of_cultivation = "pomidor",
        min_temperature = 0,
        max_temperature = 30,
        min_humidity = 20,
        max_humidity = 85)

    cultivation_2 = models.TypyOfCultivation(
        id = 2,
        name_of_cultivation = "ogórek",
        min_temperature = 5,
        max_temperature = 25,
        min_humidity = 25,
        max_humidity = 80)

    cultivations = [cultivation_1, cultivation_2]

    async with TestingSessionLocal() as db:
        db.add_all(cultivations)
        await db.commit()
        for u in cultivations:
            await db.refresh(u)  
        yield cultivations

@pytest_asyncio.fixture
async def test_data_devices():
    device_1 = models.Device(
        id = 1,
        public_id = uuid.UUID("8e8bf79e-5008-453f-b5cf-b2fb047f7360"),
        owner_id = 1,
        type_of_cultivation_id = 1,
        device_name = "Thermometer",
        device_location = "Greenhouse",
        is_email_alert_enable = False,
        device_status = "Online")

    device_2 = models.Device(
        id = 2,
        public_id = uuid.UUID("32a8d764-7f62-4c25-843c-c29b547ca3d1"),
        owner_id = 1,
        type_of_cultivation_id = 2,
        device_name = "Thermometer_2",
        device_location = "Greenhouse",
        is_email_alert_enable = True,
        device_status = "Offline")

    devices = [device_1, device_2]

    async with TestingSessionLocal() as db:
        db.add_all(devices)
        await db.commit()
        for u in devices:
            await db.refresh(u) 
        yield devices

@pytest_asyncio.fixture
async def test_data_cultivation_analyzes():
    analize = models.CultivationAnalysis(
        id = 1,
        device_id = 1,
        type_of_cultivation_id = 1,
        analysis_start_date = datetime.now(),
        analysis_end_date = None)

    async with TestingSessionLocal() as db:
        db.add(analize)
        await db.commit()
        for u in analize:
            await db.refresh(u) 
        yield analize

@pytest_asyncio.fixture
async def test_data_telemetry_data():
    telemetry_1 = models.TelemetryData(
        id = 1,
        device_id = 1,
        temperature_reading = -1,
        humidity_reading = 90,
        created_at = datetime.now())
    
    telemetry_2 = models.TelemetryData(
        id = 2,
        device_id = 1,
        temperature_reading = 20,
        humidity_reading = 50,
        created_at = datetime.now() + timedelta(minutes = 1))
    
    telemetry_3 = models.TelemetryData(
        id = 3,
        device_id = 1,
        temperature_reading = 20,
        humidity_reading = 50,
        created_at = datetime.now() + timedelta(minutes = 2))

    telemetry_4 = models.TelemetryData(
        id = 4,
        device_id = 1,
        temperature_reading = 20,
        humidity_reading = 55,
        created_at = datetime.now() + timedelta(minutes = 3))

    telemetry = [telemetry_1, telemetry_2, telemetry_3, telemetry_4]

    async with TestingSessionLocal() as db:
        db.add_all(telemetry)
        await db.commit()
        for u in telemetry:
            await db.refresh(u) 
        yield telemetry

    
@pytest_asyncio.fixture
async def test_data_audit_logs():
    log = models.AuditLog(
        id = 1,  
        user_id = 1,
        action = "CREATE NEW DEVICE",
        entity_type = "devices",
        entity_id = "8e8bf79e-5008-453f-b5cf-b2fb047f7360",
        created_at = datetime.now())

    async with TestingSessionLocal() as db:
        db.add(log)
        await db.commit()
        for u in log:
            await db.refresh(u) 
        yield log

@pytest_asyncio.fixture
async def test_data_audit_logs():
    key = models.DeviceApiKey(
        id = 1,
        device_id = q,
        token = "8e8bf79e-5008-453f-b5cf-b2fb047f7360.6119e5cb3e6014b6",
        is_active = True,
        created_at = datetime.now())

    async with TestingSessionLocal() as db:
        db.add(key)
        await db.commit()
        for u in key:
            await db.refresh(u) 
        yield key