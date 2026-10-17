from fastapi import APIRouter, Request
from starlette import status
from database.core import database_dependency
from auth.service import user_dependency
from .schemas import ChangeInformationRequest, PasswordRequest, ChangePasswordRequest
from .service import *
from core.limiter import limiter
router = APIRouter()

@router.get("/instruction", status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def get_instruction(request : Request):
    return await instruction()

@router.get("/get-user-information",status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def get_login_user_information(db : database_dependency, user : user_dependency, request : Request):
    return await get_user_information(db, user)

@router.put("/change-user-information", status_code = status.HTTP_204_NO_CONTENT)
@limiter.limit("50/minute")
async def change_user_information(user_request : ChangeInformationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_user_information(user_request, db, user)

@router.put("/change-user-password", status_code = status.HTTP_204_NO_CONTENT)
@limiter.limit("50/minute")
async def change_user_password(user_request : ChangePasswordRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_user_password(user_request, db, user)

@router.put("/reset-user-password", status_code = status.HTTP_200_OK)
@limiter.limit("50/minute")
async def reset_user_password(db : database_dependency, user : user_dependency, request : Request):
    return await reset_password(db, user)

@router.delete("/delete-user-account", status_code = status.HTTP_204_NO_CONTENT)
@limiter.limit("50/minute")
async def delete_account(user_request : PasswordRequest, db : database_dependency, user : user_dependency, request : Request):
    return await delete_user(user_request, db, user)