from utils import *
from auth.service import get_current_user, crypt_context, oauth2_password_request
from database.core import get_db
from database.models import *
from telemetry.schemas import *
from fastapi import status
import pytest
from sqlalchemy import select


@pytest.mark.asyncio
async def test_get_all_user_device_last_hour(test_data_devices, test_data_users, test_data_telemetry_data):
    app.dependency_overrides[get_db] =  override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    respons = client.get("/telemetry/get-data-based-on-selected-time-period/8e8bf79e-5008-453f-b5cf-b2fb047f7360?time=LAST_HOUR")
    assert respons.status_code == status.HTTP_200_OK
    device = respons.json()
    validate_telemetry = [TelemeterRespond.model_validate(telemetry) for telemetry in device]
    assert len(validate_telemetry) == 4

@pytest.mark.asyncio
async def test_get_all_user_device_last_half_day(test_data_devices, test_data_users, test_data_telemetry_data):

    respons = client.get("/telemetry/get-data-based-on-selected-time-period/8e8bf79e-5008-453f-b5cf-b2fb047f7360?time=LAST_HALF_DAY")
    assert respons.status_code == status.HTTP_200_OK
    device = respons.json()
    validate_telemetry = [TelemeterRespond.model_validate(telemetry) for telemetry in device]
    assert len(validate_telemetry) == 4

@pytest.mark.asyncio
async def test_get_all_user_device_last_day(test_data_devices, test_data_users, test_data_telemetry_data):

    respons = client.get("/telemetry/get-data-based-on-selected-time-period/8e8bf79e-5008-453f-b5cf-b2fb047f7360?time=LAST_DAY")
    assert respons.status_code == status.HTTP_200_OK
    device = respons.json()
    validate_telemetry = [TelemeterRespond.model_validate(telemetry) for telemetry in device]
    assert len(validate_telemetry) == 4

@pytest.mark.asyncio
async def test_get_all_user_device_last_week(test_data_devices, test_data_users, test_data_telemetry_data):

    respons = client.get("/telemetry/get-data-based-on-selected-time-period/8e8bf79e-5008-453f-b5cf-b2fb047f7360?time=LAST_WEEK")
    assert respons.status_code == status.HTTP_200_OK
    device = respons.json()
    validate_telemetry = [TelemeterRespond.model_validate(telemetry) for telemetry in device]
    assert len(validate_telemetry) == 4

@pytest.mark.asyncio
async def test_get_all_user_device_last_15_days(test_data_devices, test_data_users, test_data_telemetry_data):

    respons = client.get("/telemetry/get-data-based-on-selected-time-period/8e8bf79e-5008-453f-b5cf-b2fb047f7360?time=LAST_15_DAYS")
    assert respons.status_code == status.HTTP_200_OK
    device = respons.json()
    validate_telemetry = [TelemeterRespond.model_validate(telemetry) for telemetry in device]
    assert len(validate_telemetry) == 4

@pytest.mark.asyncio
async def test_get_all_user_device_last_month(test_data_devices, test_data_users, test_data_telemetry_data):

    respons = client.get("/telemetry/get-data-based-on-selected-time-period/8e8bf79e-5008-453f-b5cf-b2fb047f7360?time=LAST_MONTH")
    assert respons.status_code == status.HTTP_200_OK
    device = respons.json()
    validate_telemetry = [TelemeterRespond.model_validate(telemetry) for telemetry in device]
    assert len(validate_telemetry) == 4

@pytest.mark.asyncio
async def test_get_all_user_device_last_90_days(test_data_devices, test_data_users, test_data_telemetry_data):

    respons = client.get("/telemetry/get-data-based-on-selected-time-period/8e8bf79e-5008-453f-b5cf-b2fb047f7360?time=LAST_90_DAYS")
    assert respons.status_code == status.HTTP_200_OK
    device = respons.json()
    validate_telemetry = [TelemeterRespond.model_validate(telemetry) for telemetry in device]
    assert len(validate_telemetry) == 4

@pytest.mark.asyncio
async def test_get_all_user_device_when_device_not_exist(test_data_devices, test_data_users, test_data_telemetry_data):
    respons = client.get("/telemetry/get-data-based-on-selected-time-period/6445bce4-110b-450e-993e-6efcaf18f2a4?time=LAST_HOUR")
    assert respons.status_code == status.HTTP_401_UNAUTHORIZED
    data = respons.json()
    assert data["detail"] == "This device does not exist"

@pytest.mark.asyncio
async def test_get_cultivation_analize_temperature(test_data_devices, test_data_users, test_data_telemetry_data, test_data_types_of_cultivations, test_data_cultivation_analyzes):
    respons = client.get("/telemetry/get-cultivation-temperature-analyses/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_analize = AnalizeRespons.model_validate(data)
    assert validate_analize.percentage == 75

@pytest.mark.asyncio
async def test_get_cultivation_analize_temperature_when_cultivation_analize_is_end(test_data_devices, test_data_users, test_data_types_of_cultivations, test_data_cultivation_analyzes):
    client.put("/device/end-cultivation-analysis-by-user/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons = client.get("/telemetry/get-cultivation-temperature-analyses/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_analize = AnalizeRespons.model_validate(data)
    assert validate_analize.percentage == 0

@pytest.mark.asyncio
async def test_get_cultivation_analize_temperature_when_device_not_exist(test_data_devices, test_data_users, test_data_telemetry_data, test_data_types_of_cultivations, test_data_cultivation_analyzes):
    respons = client.get("/telemetry/get-cultivation-temperature-analyses/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_401_UNAUTHORIZED
    data = respons.json()
    assert data["detail"] == "This device does not exist"

@pytest.mark.asyncio
async def test_get_cultivation_analize_humidity(test_data_devices, test_data_users, test_data_telemetry_data, test_data_types_of_cultivations, test_data_cultivation_analyzes):
    respons = client.get("/telemetry/get-cultivation-humidity-analyses/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_analize = AnalizeRespons.model_validate(data)
    assert validate_analize.percentage == 75

@pytest.mark.asyncio
async def test_get_cultivation_analize_humidity_when_device_not_exist(test_data_devices, test_data_users, test_data_telemetry_data, test_data_types_of_cultivations, test_data_cultivation_analyzes):
    respons = client.get("/telemetry/get-cultivation-humidity-analyses/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_401_UNAUTHORIZED
    data = respons.json()
    assert data["detail"] == "This device does not exist"

@pytest.mark.asyncio
async def test_get_cultivation_analize_humidity_when_device_not_exist(test_data_devices, test_data_users, test_data_telemetry_data, test_data_types_of_cultivations, test_data_cultivation_analyzes):
    respons = client.get("/telemetry/get-cultivation-humidity-analyses/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_401_UNAUTHORIZED
    data = respons.json()
    assert data["detail"] == "This device does not exist"