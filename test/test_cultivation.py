from utils import *
from database.core import get_db
from database.models import *
from cultivation.schemas import *
from fastapi import status
import pytest
from sqlalchemy import select


app.dependency_overrides[get_db] =  override_get_db

@pytest.mark.asyncio
async def test_get_cultivation(test_data_types_of_cultivations):
    respons = client.get("/cultivation/all-cultivation")
    data = respons.json()
    validation = [CultivationRespond.model_validate(cultivation) for cultivation in data]
    assert validation[0].id == 1
    assert validation[0].name_of_cultivation == "pomidor"
    assert respons.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_cultivation_when_cultivation_is_not_exist():
    respons = client.get("/cultivation/all-cultivation")
    data = respons.json()
    validation = [CultivationRespond.model_validate(cultivation) for cultivation in data]
    assert validation == []
    assert respons.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_expended_cultivation(test_data_types_of_cultivations):
    respons = client.get("/cultivation/all-expended-cultivation")
    data = respons.json()
    validation = [CultivationExpendedRespons.model_validate(cultivation) for cultivation in data]
    assert validation[0].name_of_cultivation == "pomidor"
    assert validation[0].max_temperature == 30
    assert validation[0].min_temperature == 0
    assert validation[0].max_humidity == 85
    assert validation[0].min_humidity == 20
    assert respons.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_get_expended_cultivation_when_cultivation_is_not_exist():
    respons = client.get("/cultivation/all-expended-cultivation")
    data = respons.json()
    validation = [CultivationExpendedRespons.model_validate(cultivation) for cultivation in data]
    assert validation == []
    assert respons.status_code == status.HTTP_200_OK