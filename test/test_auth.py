from utils import *
from auth.service import get_current_user, crypt_context, oauth2_password_request
from database.core import get_db
from database.models import *
from auth.schemas import *
from fastapi import status
import pytest
from sqlalchemy import select


app.dependency_overrides[get_db] =  override_get_db
# app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.mark.asyncio
async def test_login_and_creating_token(test_data_users):
    respons = client.post("/token", data = {"username" : "jan123", "password" : "password"})
    data = respons.json()
    assert data.get("token_type") == "bearer"
    assert respons.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_create_new_account(test_data_users):
    request = CreateUserRequest(
            name = "Kamil",
            lastname = "Kowal",
            username = "Kam123",
            password = "Password.123456",
            email = "kamil@gmail.com"
    )
    respons = client.post("/create-account", json = request.model_dump())
    data = respons.json()
    assert respons.status_code == status.HTTP_201_CREATED
    assert data.get("message") == "Successfully created user account"

@pytest.mark.asyncio
async def test_create_new_account_when_username_exist(test_data_users):
    request = CreateUserRequest(
            name = "Kamil",
            lastname = "Kowal",
            username = "jan123",
            password = "Password.123456",
            email = "kamil@gmail.com"
    )
    respons = client.post("/create-account", json = request.model_dump())
    data = respons.json()
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    assert data.get("detail") == "Username already registered"

@pytest.mark.asyncio
async def test_create_new_account_when_email_exist(test_data_users):
    request = CreateUserRequest(
            name = "Kamil",
            lastname = "Kowal",
            username = "kam123",
            password = "Password.123456",
            email = "jan@gmail.com"
    )
    respons = client.post("/create-account", json = request.model_dump())
    data = respons.json()
    assert respons.status_code == status.HTTP_400_BAD_REQUEST
    assert data.get("detail") == "User with this email already registered"