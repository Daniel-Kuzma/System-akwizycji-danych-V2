from utils import *
from src.auth.service import get_current_user
from src.database.core import get_db
from src.database.models import *
from fastapi import status
import pytest

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user_v2

@pytest.mark.asyncio
async def test_access_to_admin_page(test_data_users):
    app.dependency_overrides[get_current_user] = lambda : {"username": "jan123", "public_id": "07c206d2-3449-451a-9cd7-86a10f6ec18f", "private_id" : 1, "role": "user"}
    request_1 = {"username" : "jan123"}
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

    request_5 = {"type_of_cultivation_id" : 1,
                 "device_name" : "Thermometer",
                 "device_location" : "GreenHouse",
                 "is_email_alert_enable" : False}

    respons_1 = client.get("/admin/all-users")
    respons_2 = client.get("/admin/user-information", params = request_1)
    respons_3 = client.put("/admin/change-user-status/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    respons_4 = client.put("/admin/change-user-role/07c206d2-3449-451a-9cd7-86a10f6ec18f", params = request_2)
    respons_5 = client.put("/admin/reset-user-password/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    respons_6 = client.delete("/admin/delete-user/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    respons_7 = client.get("/admin/audit-logs")
    respons_8 = client.get("/admin/show-all-cultivation")
    respons_9 = client.get("/admin/show-information-about-cultivation", params = request_3)
    respons_10 = client.post("/admin/add-new-cultivation", params = request_4)
    respons_11 = client.put("/admin/change-cultivation/ogórek", params = request_5)
    respons_12 = client.delete("/admin/delete-cultivation/ogórek")
    respons_13 = client.get("/admin/get-all-register-device")
    respons_14 = client.get("/admin/get-all-register-user-device/07c206d2-3449-451a-9cd7-86a10f6ec18f")
    respons_15 = client.get("/admin/get-device-information/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_16 = client.put("/admin/change-device-information/8e8bf79e-5008-453f-b5cf-b2fb047f7360", params = request_5)
    respons_17 = client.post("/admin/start-new-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_18 = client.put("/admin/end-cultivation-analysis/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_19 = client.delete("/admin/delete-register-device/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_20 = client.get("/admin/check-device-telemetry-data-logs/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_21 = client.get("/admin/get-all-device-tokens/8e8bf79e-5008-453f-b5cf-b2fb047f7360")
    respons_22 = client.put("/admin/change-status-of-device-communication-token/8e8bf79e-5008-453f-b5cf-b2fb047f7360")

    try:
        assert respons_1.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_2.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_3.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_4.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_5.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_6.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_7.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_8.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_9.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_10.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_11.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_12.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_13.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_14.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_15.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_16.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_17.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_18.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_19.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_20.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_21.status_code == status.HTTP_401_UNAUTHORIZED
        assert respons_22.status_code == status.HTTP_401_UNAUTHORIZED
    finally:
        app.dependency_overrides[get_current_user] = override_get_current_user_v2

