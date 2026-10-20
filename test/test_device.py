from utils import *
from auth.service import get_current_user, crypt_context, oauth2_password_request
from database.core import get_db
from database.models import *
from device.schemas import *
from fastapi import status
import pytest
from sqlalchemy import select




@pytest.mark.asyncio
async def test_get_all_user_device(test_data_devices, test_data_users, test_data_types_of_cultivations):
    app.dependency_overrides[get_db] =  override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    respons = client.get("/device/all-user-device")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()

    assert len(data) == 2
    assert data[0].get("device_name") == "Thermometer"
    assert data[1].get("device_name") == "Thermometer_2"

@pytest.mark.asyncio
async def test_get_all_user_device_when_user_has_none_device():
    respons = client.get("/device/all-user-device")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    valid_device = [AllUserDeviceResponse.model_validate(device) for device in data]
    assert valid_device == []

@pytest.mark.asyncio
async def test_get_device_information(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.get("/device/user-device/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()

    assert data.get("device_name") == "Thermometer"

@pytest.mark.asyncio
async def test_get_user_device_information_when_device_not_exist(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.get("/device/user-device/168c42bd-6933-4597-a384-fbcc0b7c656b")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_create_new_device(test_data_devices, test_data_api_keys, test_data_users, test_data_types_of_cultivations):
    request = DeviceRequest(type_of_cultivation = 1,
                            device_name = "test",
                            device_location = "test_location",
                            is_email_alert_enable = False)
    respons = client.post("/device/create-new-device", json = request.model_dump())
    assert respons.status_code == status.HTTP_201_CREATED
    data = respons.json()
    token = data["message"][-53:]
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(DeviceApiKey.token).where(DeviceApiKey.device_id == 3).limit(1))
        result = stmt.scalar()
        assert crypt_context.verify(token, result) == True
    


@pytest.mark.asyncio
async def test_change_device_information(test_data_devices, test_data_users, test_data_types_of_cultivations):
    request = ChangeDeviceInformationRequest(
                type_of_cultivation_id = 1,
                device_name = "Thermometer_Green",
                device_location = "Greenhouse",
                is_email_alert_enable = True)
    respons = client.put("/device/change-device-information/8e8bf79e-5008-453f-b5cf-b2fb047f7360", json = request.model_dump())
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully updated device information"
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(Device).where(Device.id == 1).limit(1))
        result = stmt.scalar()
        assert result.device_name == "Thermometer_Green"

@pytest.mark.asyncio
async def test_change_device_information_when_analize_is_not_end(test_data_devices, test_data_users, test_data_types_of_cultivations, test_data_cultivation_analyzes):
    request = ChangeDeviceInformationRequest(
                type_of_cultivation_id = 2,
                device_name = "Thermometer_Green",
                device_location = "Greenhouse",
                is_email_alert_enable = True)
    respons = client.put("/device/change-device-information/8e8bf79e-5008-453f-b5cf-b2fb047f7360", json = request.model_dump())
    assert respons.status_code == status.HTTP_403_FORBIDDEN
    data = respons.json()
    assert data["detail"] == "If you want to start new analize you need to end last cultivation analysis"

@pytest.mark.asyncio
async def test_change_device_information_when_device_not_exist(test_data_devices, test_data_users, test_data_types_of_cultivations):
    request = ChangeDeviceInformationRequest(
                type_of_cultivation_id = 2,
                device_name = "Thermometer_Green",
                device_location = "Greenhouse",
                is_email_alert_enable = True)
    respons = client.put("/device/change-device-information/e4dba622-fb2a-471c-8dce-5c49057c5b69", json = request.model_dump())
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_create_new_cultivation_analysis(test_data_devices, test_data_cultivation_analyzes):
    client.put("/device/end-cultivation-analysis-by-user/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons = client.post("/device/start-new-cultivation-analysis-by-user/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_201_CREATED
    data = respons.json()
    assert data["message"] == "Start new cultivation analysis"

@pytest.mark.asyncio
async def test_create_new_cultivation_analysis_when_analize_is_not_end(test_data_devices, test_data_cultivation_analyzes):
    respons = client.post("/device/start-new-cultivation-analysis-by-user/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_403_FORBIDDEN
    data = respons.json()
    assert data["detail"] == "If you want to start new analize you need to end last cultivation analysis"

@pytest.mark.asyncio
async def test_create_new_cultivation_analysis_when_device_not_exist(test_data_devices, test_data_cultivation_analyzes):
    respons = client.post("/device/start-new-cultivation-analysis-by-user/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_stop_cultivation_analysis(test_data_devices, test_data_cultivation_analyzes):
    respons = client.put("/device/end-cultivation-analysis-by-user/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully end cultivation analysis"

@pytest.mark.asyncio
async def test_stop_cultivation_analysis_when_analize_is_already_end(test_data_devices, test_data_cultivation_analyzes):
    client.put("/device/end-cultivation-analysis-by-user/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons = client.put("/device/end-cultivation-analysis-by-user/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Already end cultivation analyze"

@pytest.mark.asyncio
async def test_stop_cultivation_analysis_when_analize_is_not_started(test_data_devices, test_data_cultivation_analyzes):
    respons = client.put("/device/end-cultivation-analysis-by-user/32a8d764-7f62-4c25-843c-c29b547ca3d1")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "There is no active analysis"

@pytest.mark.asyncio
async def test_stop_cultivation_analysis_when_device_not_exist(test_data_devices, test_data_cultivation_analyzes):
    respons = client.put("/device/end-cultivation-analysis-by-user/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_update_device_token(test_data_devices, test_data_api_keys):
    respons = client.put("/device/generate-new-key-for-device/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    token = data.get("token")
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(DeviceApiKey.token).where(DeviceApiKey.device_id == 1).limit(1))
        result = stmt.scalar()
        print(result)
        assert crypt_context.verify(token, result) == True

@pytest.mark.asyncio
async def test_update_device_token_when_device_not_exist(test_data_devices, test_data_api_keys):
    respons = client.put("/device/generate-new-key-for-device/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"
    

@pytest.mark.asyncio
async def test_change_token_status(test_data_api_keys, test_data_devices):
    respons = client.put("/device/change-device-token-activity/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    data = respons.json()
    assert respons.status_code == status.HTTP_200_OK
    assert data["message"] == "Successfully updated device token activity"
    async with TestingSessionLocal() as db:
        stmt = db = await db.execute(select(DeviceApiKey.is_active).where(DeviceApiKey.device_id == 1).limit(1))
        result = stmt.scalar()
        assert result == False

@pytest.mark.asyncio
async def test_change_token_status_when_device_not_exist(test_data_api_keys, test_data_devices):
    respons = client.put("/device/change-device-token-activity/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_delete_register_device(test_data_devices, test_data_users, test_data_types_of_cultivations):
    request = DeviceNameRequest(device_name = "Thermometer")
    respons = client.request("DELETE", "/device/delete-device/8e8bf79e-5008-453f-b5cf-b2fb047f7360", json = request.model_dump())
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully delete device"

@pytest.mark.asyncio
async def test_delete_register_device_with_bad_name_of_device(test_data_devices, test_data_users, test_data_types_of_cultivations):
    request = DeviceNameRequest(device_name = "Thermometer123")
    respons = client.request("DELETE", "/device/delete-device/8e8bf79e-5008-453f-b5cf-b2fb047f7360", json = request.model_dump())
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Provides the correct name of device"

@pytest.mark.asyncio
async def test_delete_register_device_when_device_not_exist(test_data_devices, test_data_users, test_data_types_of_cultivations):
    request = DeviceNameRequest(device_name = "Thermometer")
    respons = client.request("DELETE", "/device/delete-device/6445bce4-110b-450e-993e-6efcaf18f2a4", json = request.model_dump())
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"