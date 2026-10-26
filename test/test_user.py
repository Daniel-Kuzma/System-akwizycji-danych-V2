from utils import *
from auth.service import get_current_user, crypt_context, oauth2_password_request
from database.core import get_db
from database.models import *
from users.schemas import *
from fastapi import status
import pytest
from sqlalchemy import select


@pytest.mark.asyncio
async def test_get_all_user_device_last_hour(test_data_users):
    app.dependency_overrides[get_db] =  override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    respons = client.get("/users/instruction")
    data = respons.json()
    print(data)
    assert data["message"] == "soon"
    assert respons.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_user_information(test_data_users):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    respons = client.get("/users/get-user-information")
    app.dependency_overrides.clear()
    data = respons.json()
    print(data)
    validate_user = UserInformationRespond.model_validate(data)
    assert validate_user.name == "Jan"
    assert respons.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_change_user_information(test_data_users):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    request = ChangeInformationRequest(name = "Jan", lastname = "Kowalski", username = "jan1234", email = "jan@gamil.com")
    respons = client.put("/users/change-user-information", json = request.model_dump())
    app.dependency_overrides.clear()
    data = respons.json()
    assert respons.status_code == status.HTTP_200_OK
    assert data["message"] == "Successfully changed account information"
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(User).where(User.id == 1).limit(1))
        result = stmt.scalar()
        assert result.username == "jan1234"

@pytest.mark.asyncio
async def test_get_change_user_information_with_username_which_already_exist(test_data_users):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    request = ChangeInformationRequest(name = "Jan", lastname = "Kowalski", username = "admin", email = "jan@gmail.com")
    respons = client.put("/users/change-user-information", json = request.model_dump())
    app.dependency_overrides.clear()
    data = respons.json()
    assert respons.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "User with this username already exist"

@pytest.mark.asyncio
async def test_get_change_user_information_with_email_which_already_exist(test_data_users):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    request = ChangeInformationRequest(name = "Jan", lastname = "Kowalski", username = "jan123", email = "admin@gmail.com")
    respons = client.put("/users/change-user-information", json = request.model_dump())
    app.dependency_overrides.clear()
    data = respons.json()
    assert respons.status_code == status.HTTP_409_CONFLICT
    assert data["detail"] == "User with this email already exist"

@pytest.mark.asyncio
async def test_change_user_password(test_data_users):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    request = ChangePasswordRequest(old_password = "password", new_password = "Password1.com")
    respons = client.put("/users/change-user-password", json = request.model_dump())
    app.dependency_overrides.clear()
    data = respons.json()
    assert respons.status_code == status.HTTP_200_OK
    assert data["message"] == "Successfully changed password"
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(User.password).where(User.id == 1).limit(1))
        result = stmt.scalar()
        assert crypt_context.verify("Password1.com", result)

@pytest.mark.asyncio
async def test_change_user_password_when_you_put_bad_password(test_data_users):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    request = ChangePasswordRequest(old_password = "password123", new_password = "Password1.com")
    respons = client.put("/users/change-user-password", json = request.model_dump())
    app.dependency_overrides.clear()
    data = respons.json()
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "You provide wrong password. Try again"

# @pytest.mark.asyncio
# async def test_reset_user_password(test_data_users):
#     app.dependency_overrides[get_db] = override_get_db
#     app.dependency_overrides[get_current_user] = override_get_current_user
#     respons = client.put("/users/reset-user-password")
#     app.dependency_overrides.clear()
#     assert respons.status_code == status.HTTP_200_OK
#     async with TestingSessionLocal() as db:
#         stmt = await db.execute(select(User.password).where(User.id == 1).limit(1))
#         result = stmt.scalar()
#         assert crypt_context.verify("password", result) == False

@pytest.mark.asyncio
async def test_delete_account(test_data_users):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    request = PasswordRequest(password = "password")
    respons = client.request("DELETE", "/users/delete-user-account", json = request.model_dump())
    app.dependency_overrides.clear()
    data = respons.json()
    assert data["message"] == "Successfully deleted account"
    assert respons.status_code == status.HTTP_200_OK
    async with TestingSessionLocal() as db:
        stmt = await db.execute(select(User).where(User.id == 1).limit(1))
        result = stmt.one_or_none()
        assert result == None

@pytest.mark.asyncio
async def test_delete_account_with_bad_password(test_data_users):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    request = PasswordRequest(password = "password1")
    respons = client.request("DELETE", "/users/delete-user-account", json = request.model_dump())
    app.dependency_overrides.clear()
    data = respons.json()
    assert data["detail"] == "You provide wrong password. Try again"
    assert respons.status_code == status.HTTP_400_BAD_REQUEST