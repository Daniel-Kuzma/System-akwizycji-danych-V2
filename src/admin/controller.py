from fastapi import APIRouter, Request
from starlette import status
from database.core import database_dependency
from auth.service import user_dependency
from schemas import CultivationRequest, RoleRequest
from service import *
from typing import Optional

router = APIRouter()

@router.get("/all-users", status_code = status.HTTP_200_OK)
async def all_users(db : database_dependency, user : user_dependency, request : Request):
    return await get_all_users(db, user)

@router.get("/user-information/{public_id}", status_code = status.HTTP_200_OK)
async def all_users(public_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await get_user(public_id, db, user)

@router.put("/change-user-status/{public_id}", status_code = status.HTTP_204_NO_CONTENT)
async def change_user_status(public_id : str, new_status : bool, db : database_dependency, user : user_dependency, request : Request):
    return await update_user_status(public_id, new_status, db, user)
    
@router.put("/change-user-role/{public_id}", status_code = status.HTTP_204_NO_CONTENT)
async def change_user_role(public_id : str, new_role : RoleRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_user_role(db, new_role, user, public_id)
    
@router.delete("/delete-user/{public_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(public_id : str, db : database_dependency, user : user_dependency, request : Request):
    return await delete(db, user, public_id)

@router.get("/audit-logs")
async def audit_logs(db : database_dependency, user : user_dependency, request : Request, user_id_for_logs : Optional[str] = None):
    return await get_audit_logs(user_id_for_logs, db, user)

@router.get("/show-typ-of-cultivation", status_code = status.HTTP_200_OK)
async def new_cultivation(db : database_dependency, user : user_dependency, request : Request, cultivation_type : Optional[str] = None):
    return await get_cultivations(cultivation_type, db, user)

@router.post("/add-new-cultivation-type", status_code = status.HTTP_201_CREATED)
async def new_cultivation(cultivation_request : CultivationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await add_new_cultivation(cultivation_request, db, user)

@router.put("/change-cultivation-type/{type_of_cultivation}", status_code = status.HTTP_204_NO_CONTENT)
async def new_cultivation(type_of_cultivation : str, cultivation_request : CultivationRequest, db : database_dependency, user : user_dependency, request : Request):
    return await update_cultivation(type_of_cultivation, cultivation_request, db, user)

@router.put("/delete-cultivation-type/{type_of_cultivation}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_cultivation(type_of_cultivation : str, db : database_dependency, user : user_dependency, request : Request):
    return await delete_cult_type(type_of_cultivation, db, user)