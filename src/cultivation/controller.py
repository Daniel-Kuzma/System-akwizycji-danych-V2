from fastapi import APIRouter, Request
from starlette import status
from core.limiter import limiter
from database.core import database_dependency
from .schemas import CultivationRespond, CultivationExpendedRespons
from .service import get_cultivation

router = APIRouter()

@limiter.limit("50/minute")
@router.get("/all-cultivation", response_model = list[CultivationRespond], status_code = status.HTTP_200_OK)
async def get_all_cultivation(db : database_dependency, request : Request):
    return await get_cultivation(db)

@limiter.limit("50/minute")
@router.get("/all-expended-cultivation", response_model = list[CultivationExpendedRespons], status_code = status.HTTP_200_OK)
async def get_all_expended_cultivation(db : database_dependency, request : Request):
    return await get_cultivation(db)