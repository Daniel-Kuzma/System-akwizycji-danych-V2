from utils import *
from auth.service import get_current_user, crypt_context
from database.core import get_db
from database.models import *
from admin.schemas import *
from fastapi import status
import pytest
from sqlalchemy import select


app.dependency_overrides[get_db] =  override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user_v2

@pytest.mark.asyncio
async def test_access_to_admin_page(test_data_users):
    app.dependency_overrides[get_current_user] = override_get_current_user
    request_2 = {"role" : "admin"}
    request_3 = {"cultivation_type" : "pomidor"}
    request_4 = {"name_of_cultivation" : "ziemniak",
                 "min_temperature" : 1,
                 "max_temperature" : 2,
                 "min_humidity" : 1,
                 "max_humidity" : 80}
    
    request_5 = {"name_of_cultivation" : "ziemniak",
                 "min_temperature" : 1,
                 "max_temperature" : 2,
                 "min_humidity" : 10,
                 "max_humidity" : 80}

    request_6 = {"type_of_cultivation_id" : 1,
                 "device_name" : "Thermometer",
                 "device_location" : "GreenHouse",
                 "is_email_alert_enable" : False}

    respons_1 = client.get("/admin/all-users")
    respons_2 = client.get("/admin/user-information?07c206d2-3449-451a-9cd7-86a10f6ec18f")
    respons_3 = client.put("/admin/change-user-status/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    respons_4 = client.put("/admin/change-user-role/07c206d2-3449-451a-9cd7-86a10f6ec18f", json = request_2)
    respons_5 = client.put("/admin/reset-user-password/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    respons_6 = client.delete("/admin/delete-user/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    respons_7 = client.get("/admin/audit-logs")
    respons_8 = client.get("/admin/show-all-cultivation")
    respons_9 = client.get("/admin/show-information-about-cultivation", params = request_3)
    respons_10 = client.post("/admin/add-new-cultivation", json = request_4)
    respons_11 = client.put("/admin/change-cultivation/ogórek", json = request_5)
    respons_12 = client.delete("/admin/delete-cultivation/ogórek")
    respons_13 = client.get("/admin/get-all-register-device")
    respons_14 = client.get("/admin/get-all-register-user-device/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    respons_15 = client.get("/admin/get-device-information/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_16 = client.put("/admin/change-device-information/8e8bf79e-5008-453f-b5cf-b2fb047f7360", json = request_6)
    respons_17 = client.post("/admin/start-new-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_18 = client.put("/admin/end-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_20 = client.get("/admin/check-device-telemetry-data-logs/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_21 = client.get("/admin/get-all-device-tokens/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_22 = client.put("/admin/change-status-of-device-communication-token/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_19 = client.delete("/admin/delete-register-device/8e8bf79e-5008-453f-b5cf-b2fb047f7360")


    assert respons_1.status_code == status.HTTP_403_FORBIDDEN
    assert respons_2.status_code == status.HTTP_403_FORBIDDEN
    assert respons_3.status_code == status.HTTP_403_FORBIDDEN
    assert respons_4.status_code == status.HTTP_403_FORBIDDEN
    assert respons_5.status_code == status.HTTP_403_FORBIDDEN
    assert respons_6.status_code == status.HTTP_403_FORBIDDEN
    assert respons_7.status_code == status.HTTP_403_FORBIDDEN
    assert respons_8.status_code == status.HTTP_403_FORBIDDEN
    assert respons_9.status_code == status.HTTP_403_FORBIDDEN
    assert respons_10.status_code == status.HTTP_403_FORBIDDEN
    assert respons_11.status_code == status.HTTP_403_FORBIDDEN
    assert respons_12.status_code == status.HTTP_403_FORBIDDEN
    assert respons_13.status_code == status.HTTP_403_FORBIDDEN
    assert respons_14.status_code == status.HTTP_403_FORBIDDEN
    assert respons_15.status_code == status.HTTP_403_FORBIDDEN
    assert respons_16.status_code == status.HTTP_403_FORBIDDEN
    assert respons_17.status_code == status.HTTP_403_FORBIDDEN
    assert respons_18.status_code == status.HTTP_403_FORBIDDEN
    assert respons_19.status_code == status.HTTP_403_FORBIDDEN
    assert respons_20.status_code == status.HTTP_403_FORBIDDEN
    assert respons_21.status_code == status.HTTP_403_FORBIDDEN
    assert respons_22.status_code == status.HTTP_403_FORBIDDEN
        
    app.dependency_overrides[get_current_user] = override_get_current_user_v2

@pytest.mark.asyncio
async def test_get_all_users(test_data_users):
    respons = client.get("/admin/all-users")
    assert respons.status_code == status.HTTP_200_OK

    data = respons.json()
    validate_user = [UserRespons.model_validate(user) for user in data]

    assert validate_user[0].username == "jan123"
    assert validate_user[1].username == "admin"

@pytest.mark.asyncio
async def test_get_all_users_where_is_none_user():
    respons = client.get("/admin/all-users")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_user = [UserRespons.model_validate(user) for user in data]
    assert validate_user == []

@pytest.mark.asyncio
async def test_get_user_information_by_public_id(test_data_users):
    request = {"public_id" : "07c206d2-3449-451a-9cd7-86a10f6ec18f"}
    respons = client.get("/admin/user-information/", params = request)
    assert respons.status_code == status.HTTP_200_OK

    data = respons.json()
    validate_user = UserRespons.model_validate(data)

    assert validate_user.username == "jan123"

@pytest.mark.asyncio
async def test_get_user_information_by_username(test_data_users):
    request = {"username" : "jan123"}
    respons = client.get("/admin/user-information/", params = request)
    assert respons.status_code == status.HTTP_200_OK

    data = respons.json()
    validate_user = UserRespons.model_validate(data)

    assert validate_user.username == "jan123"

@pytest.mark.asyncio
async def test_get_user_information_by_email(test_data_users):
    request = {"email" : "jan@gmail.com"}
    respons = client.get("/admin/user-information/", params = request)
    assert respons.status_code == status.HTTP_200_OK

    data = respons.json()
    validate_user = UserRespons.model_validate(data)

    assert validate_user.username == "jan123"

@pytest.mark.asyncio
async def test_get_user_information_when_user_not_exist(test_data_users):
    request = {"username" : "jan12345"}
    respons = client.get("/admin/user-information/", params = request)
    data = respons.json()
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "User dose not exist"

@pytest.mark.asyncio
async def test_change_user_status(test_data_users):
    respons = client.put("/admin/change-user-status/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully changed user status"
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(User.is_active).where(User.public_id == uuid.UUID("07c206d2-3449-451a-9cd7-86a10f6ec18f")).limit(1))
        result = stmt.scalar()
        assert result == False

@pytest.mark.asyncio
async def test_change_user_status_when_user_not_exist(test_data_users):
    respons = client.put("/admin/change-user-status/32806820-9272-48a4-9414-c2484ff50af9")
    data = respons.json()
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "User with this public id dose not exist"

@pytest.mark.asyncio
async def test_change_user_role(test_data_users):
    request = RoleRequest(
        role = RoleEnum.ADMIN
    )
    respons = client.put("/admin/change-user-role/07c206d2-3449-451a-9cd7-86a10f6ec18f", json = request.model_dump())
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully changed user role"
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(User.user_role).where(User.public_id == uuid.UUID("07c206d2-3449-451a-9cd7-86a10f6ec18f")).limit(1))
        result = stmt.scalar()
        assert result == "admin"

@pytest.mark.asyncio
async def test_change_user_role_when_user_not_exist(test_data_users):
    request = RoleRequest(
        role = RoleEnum.ADMIN
    )
    respons = client.put("/admin/change-user-role/32806820-9272-48a4-9414-c2484ff50af9", json = request.model_dump())
    data = respons.json()
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "User with this public id dose not exist"


# @pytest.mark.asyncio
# async def test_change_user_password(test_data_users):
#     respons = client.put("/admin/reset-user-password/07c206d2-3449-451a-9cd7-86a10f6ec18f")
#     assert respons.status_code == status.HTTP_200_OK
#     async with TestingSessionLocal() as db:
#         stmt = await db.execute(select(User.password).where(User.public_id == uuid.UUID("07c206d2-3449-451a-9cd7-86a10f6ec18f")).limit(1))
#         result = stmt.scalar()
#         assert crypt_context.verify("password", result) == False

# @pytest.mark.asyncio
# async def test_change_user_password_when_user_not_exist(test_data_users):
#     respons = client.put("/admin/reset-user-password/32806820-9272-48a4-9414-c2484ff50af9")
#     data = respons.json()
#     assert respons.status_code == status.HTTP_400_BAD_REQUEST
#     assert data["detail"] == "User with this public id dose not exist"

@pytest.mark.asyncio
async def test_delete_user(test_data_users):
    respons = client.delete("/admin/delete-user/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully deleted user"
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(User).where(User.public_id == uuid.UUID("07c206d2-3449-451a-9cd7-86a10f6ec18f")).limit(1))
        result = stmt.one_or_none()
        assert result == None

@pytest.mark.asyncio
async def test_delete_user_when_user_not_exist(test_data_users):
    respons = client.delete("/admin/delete-user/32806820-9272-48a4-9414-c2484ff50af9")
    data = respons.json()
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "User with this public id dose not exist"

@pytest.mark.asyncio
async def test_get_audit_logs_by_device_public_id(test_data_audit_logs, test_data_users, test_data_devices):
    request = {"device_public_id" : "8e8bf79e-5008-453f-b5cf-b2fb047f7360"}
    respons = client.get("/admin/audit-logs", params = request)
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_logs = [AudiLogResponse.model_validate(logs) for logs in data]
    assert validate_logs[0].entity_type == "devices"

@pytest.mark.asyncio
async def test_get_audit_logs_user_id_for_logs(test_data_audit_logs, test_data_users):
    request = {"user_id_for_logs" : "07c206d2-3449-451a-9cd7-86a10f6ec18f"}
    respons = client.get("/admin/audit-logs", params = request)
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_logs = [AudiLogResponse.model_validate(logs) for logs in data]
    assert validate_logs[0].entity_type == "devices"

@pytest.mark.asyncio
async def test_get_audit_logs(test_data_audit_logs, test_data_users):
    respons = client.get("/admin/audit-logs")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_user = [AudiLogResponse.model_validate(logs) for logs in data]
    assert validate_user[0].entity_type == "devices"

@pytest.mark.asyncio
async def test_get_audit_logs_when_is_empty():
    respons = client.get("/admin/audit-logs")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_logs = [AudiLogResponse.model_validate(logs) for logs in data]
    assert validate_logs == []

@pytest.mark.asyncio
async def test_get_all_cultivations(test_data_types_of_cultivations):
    respons = client.get("/admin/show-all-cultivation")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_cultivation = [CultivationRespons.model_validate(cult) for cult in data]
    assert validate_cultivation[0].name_of_cultivation == "pomidor"
    assert validate_cultivation[1].name_of_cultivation == "ogórek"

@pytest.mark.asyncio
async def test_get_all_cultivations_when_is_none_cultivation():
    respons = client.get("/admin/show-all-cultivation")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_cultivation = [CultivationRespons.model_validate(cult) for cult in data]
    assert validate_cultivation == []

@pytest.mark.asyncio
async def test_get_cultivation(test_data_types_of_cultivations):
    request = {"cultivation_type" : "pomidor"}
    respons = client.get("/admin/show-information-about-cultivation", params = request)
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    validate_cultivation = CultivationRespons.model_validate(data)
    assert validate_cultivation.name_of_cultivation == "pomidor"

@pytest.mark.asyncio
async def test_get_cultivation_when_cultivation_not_exist(test_data_types_of_cultivations):
    request = {"cultivation_type" : "ziemniak"}
    respons = client.get("/admin/show-information-about-cultivation", params = request)
    data = respons.json()
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "This type of cultivation dose not exist"

@pytest.mark.asyncio
async def test_add_cultivation(test_data_types_of_cultivations):
    request = CultivationRequest(
            name_of_cultivation = "ziemniak",
            min_temperature = 10,
            max_temperature = 15,
            min_humidity = 34,
            max_humidity = 80)
    respons = client.post("/admin/add-new-cultivation", json = request.model_dump())
    assert respons.status_code == status.HTTP_201_CREATED
    data = respons.json()
    assert data["message"] == "Successfully added new cultivation type"
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(TypyOfCultivation.name_of_cultivation).where(TypyOfCultivation.id == 3).limit(1))
        result = stmt.scalar()
        assert result == "ziemniak"

@pytest.mark.asyncio
async def test_add_cultivation_when_cultivation_already_exist(test_data_types_of_cultivations):
    request = CultivationRequest(
            name_of_cultivation = "pomidor",
            min_temperature = 10,
            max_temperature = 15,
            min_humidity = 34,
            max_humidity = 80)
    respons = client.post("/admin/add-new-cultivation", json = request.model_dump())
    assert respons.status_code == status.HTTP_409_CONFLICT
    data = respons.json()
    assert data["detail"] == "This cultivation already exist"

@pytest.mark.asyncio
async def test_change_cultivation(test_data_types_of_cultivations):
    request = CultivationRequest(
            name_of_cultivation = "pomidor",
            min_temperature = 10,
            max_temperature = 15,
            min_humidity = 34,
            max_humidity = 80)
    respons = client.put("/admin/change-cultivation/pomidor", json = request.model_dump())
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully updated cultivation"

@pytest.mark.asyncio
async def test_change_cultivation_when_cultivation_not_exist(test_data_types_of_cultivations):
    request = CultivationRequest(
            name_of_cultivation = "ziemniak",
            min_temperature = 10,
            max_temperature = 15,
            min_humidity = 34,
            max_humidity = 80)
    respons = client.put("/admin/change-cultivation/ziemniak", json = request.model_dump())
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "This cultivation dose not exist"

@pytest.mark.asyncio
async def test_delete_cultivation(test_data_types_of_cultivations):
    respons = client.delete("/admin/delete-cultivation/ogórek")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully deleted cultivation"

@pytest.mark.asyncio
async def test_delete_cultivation_when_cultivation_not_exist(test_data_types_of_cultivations):
    respons = client.delete("/admin/delete-cultivation/ziemniak")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "This cultivation dose not exist"

@pytest.mark.asyncio
async def test_get_all_device(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.get("/admin/get-all-register-device")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()

    assert len(data) == 2
    assert data[0].get("device_name") == "Thermometer"
    assert data[1].get("device_name") == "Thermometer_2"

@pytest.mark.asyncio
async def test_get_all_device_when_is_none_device():
    respons = client.get("/admin/get-all-register-device")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    valid_device = [AllDeviceResponse.model_validate(device) for device in data]
    assert valid_device == []

@pytest.mark.asyncio
async def test_get_all_user_device(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.get("/admin/get-all-register-user-device/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert len(data) == 2
    assert data[0].get("device_name") == "Thermometer"

@pytest.mark.asyncio
async def test_get_all_user_device_when_user_has_none_device(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.get("/admin/get-all-register-user-device/70f41b40-a522-4ba8-b1cd-ab6a1ca7febd")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data == []

@pytest.mark.asyncio
async def test_get_all_user_device_when_user_not_exist(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.get("/admin/get-all-register-user-device/5a000a04-640b-4ba2-a58b-359562ff99d4")
    data = respons.json()
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "User with this public id dose not exist"

@pytest.mark.asyncio
async def test_get_device_information(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.get("/admin/get-device-information/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    valid_device = [DeviceInformationResponse.model_validate(device) for device in data]
    assert valid_device[0].device_name == "Thermometer"

@pytest.mark.asyncio
async def test_get_device_information_when_device_not_exist(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.get("/admin/get-device-information/168c42bd-6933-4597-a384-fbcc0b7c656b")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_change_device_information(test_data_devices, test_data_users, test_data_types_of_cultivations):
    request = NewDeviceInformationRequest(
                type_of_cultivation_id = 1,
                device_name = "Thermometer_Green",
                device_location = "Greenhouse"  ,
                is_email_alert_enable = True)
    respons = client.put("/admin/change-device-information/8e8bf79e-5008-453f-b5cf-b2fb047f7360", json = request.model_dump())
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully changed device information"
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(Device).where(Device.public_id == uuid.UUID("8e8bf79e-5008-453f-b5cf-b2fb047f7360")).limit(1))
        result = stmt.scalar()
        assert result.device_name == "Thermometer_Green"

@pytest.mark.asyncio
async def test_change_device_information_when_analize_is_not_end(test_data_devices, test_data_users, test_data_types_of_cultivations, test_data_cultivation_analyzes):
    request = NewDeviceInformationRequest(
                type_of_cultivation_id = 2,
                device_name = "Thermometer_Green",
                device_location = "Greenhouse"  ,
                is_email_alert_enable = True)
    respons = client.put("/admin/change-device-information/8e8bf79e-5008-453f-b5cf-b2fb047f7360", json = request.model_dump())
    assert respons.status_code == status.HTTP_403_FORBIDDEN
    data = respons.json()
    assert data["detail"] == "If you want to change cultivation type you need to end cultivation analysis"

@pytest.mark.asyncio
async def test_change_device_information_when_device_not_exist(test_data_devices, test_data_users, test_data_types_of_cultivations):
    request = NewDeviceInformationRequest(
                type_of_cultivation_id = 2,
                device_name = "Thermometer_Green",
                device_location = "Greenhouse"  ,
                is_email_alert_enable = True)
    respons = client.put("/admin/change-device-information/e4dba622-fb2a-471c-8dce-5c49057c5b69", json = request.model_dump())
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_create_new_cultivation_analysis(test_data_devices, test_data_cultivation_analyzes):
    client.put("/admin/end-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons = client.post("/admin/start-new-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_201_CREATED
    data = respons.json()
    assert data["message"] == "Start new cultivation analysis"

@pytest.mark.asyncio
async def test_create_new_cultivation_analysis_when_analize_is_not_end(test_data_devices, test_data_cultivation_analyzes):
    respons = client.post("/admin/start-new-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_403_FORBIDDEN
    data = respons.json()
    assert data["detail"] == "If you want to start new analize you need to end last cultivation analysis"

@pytest.mark.asyncio
async def test_create_new_cultivation_analysis_when_device_not_exist(test_data_devices, test_data_cultivation_analyzes):
    respons = client.post("/admin/start-new-cultivation-analysis/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_stop_cultivation_analysis(test_data_devices, test_data_cultivation_analyzes):
    respons = client.put("/admin/end-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully end cultivation analysis"

@pytest.mark.asyncio
async def test_stop_cultivation_analysis_when_analize_is_already_end(test_data_devices, test_data_cultivation_analyzes):
    client.put("/admin/end-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons = client.put("/admin/end-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Already end cultivation analyze"

@pytest.mark.asyncio
async def test_stop_cultivation_analysis_when_analize_is_not_started(test_data_devices, test_data_cultivation_analyzes):
    respons = client.put("/admin/end-cultivation-analysis/32a8d764-7f62-4c25-843c-c29b547ca3d1")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "There is no active analysis"

@pytest.mark.asyncio
async def test_stop_cultivation_analysis_when_device_not_exist(test_data_devices, test_data_cultivation_analyzes):
    respons = client.put("/admin/end-cultivation-analysis/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_delete_register_device(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.delete("/admin/delete-register-device/32a8d764-7f62-4c25-843c-c29b547ca3d1")
    assert respons.status_code == status.HTTP_200_OK
    data = respons.json()
    assert data["message"] == "Successfully delete device"

@pytest.mark.asyncio
async def test_delete_register_device_when_device_not_exist(test_data_devices, test_data_users, test_data_types_of_cultivations):
    respons = client.delete("/admin/delete-register-device/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_check_device_data_logs(test_data_telemetry_data, test_data_devices):
    respons = client.get("/admin/check-device-telemetry-data-logs/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    data = respons.json()
    validate_telemetry_logs = [TelemetryDataResponse.model_validate(logs) for logs in data]
    assert respons.status_code == status.HTTP_200_OK
    assert len(validate_telemetry_logs) == 4

@pytest.mark.asyncio
async def test_check_device_data_logs_when_device_not_exist(test_data_telemetry_data, test_data_devices):
    respons = client.get("/admin/check-device-telemetry-data-logs/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_get_device_token(test_data_api_keys, test_data_devices, ):
    respons = client.get("/admin/get-all-device-tokens/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    data = respons.json()
    print(data)
    assert respons.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert data[0].get("is_active") == True

@pytest.mark.asyncio
async def test_get_device_token_when_device_not_exist(test_data_api_keys, test_data_devices):
    respons = client.get("/admin/get-all-device-tokens/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"

@pytest.mark.asyncio
async def test_change_token_status(test_data_api_keys, test_data_devices):
    respons = client.put("/admin/change-status-of-device-communication-token/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    data = respons.json()
    assert respons.status_code == status.HTTP_200_OK
    assert data["message"] == "Successfully change token status"
    async with TestingSessionLocal() as db:
        stmt = db = await db.execute(select(DeviceApiKey.is_active).where(DeviceApiKey.device_id == 1).limit(1))
        result = stmt.scalar()
        assert result == False

@pytest.mark.asyncio
async def test_change_token_status_when_device_not_exist(test_data_api_keys, test_data_devices):
    respons = client.put("/admin/change-status-of-device-communication-token/6445bce4-110b-450e-993e-6efcaf18f2a4")
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    data = respons.json()
    assert data["detail"] == "Device with this public id dose not exist"