from fastapi import APIRouter, Request, HTTPException
from starlette import status
from database.core import database_dependency
from auth.service import user_dependency
from schemas import CultivationRequest
from service import get_all_users, update_user_role, update_user_status, delete, get_audit_logs, add_new_cultivation


router = APIRouter()

@router.get("/all-users", status_code = status.HTTP_200_OK)
async def all_users(db : database_dependency, user : user_dependency, request : Request):
    try:
        all_users = await get_all_users(db, user)
        return all_users
    except HTTPException:
        pass

@router.put("/change-user-status/{public_id}", status_code = status.HTTP_204_NO_CONTENT)
async def change_user_status(public_id : str, db : database_dependency, user : user_dependency, request : Request):
    await update_user_status(db, user, public_id)


@router.put("/change-user-role/{public_id}", status_code = status.HTTP_204_NO_CONTENT)
async def change_user_role(public_id : str,db : database_dependency, user : user_dependency, request : Request):
    await update_user_role(db, user, public_id)


@router.delete("/delete-user/{public_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(public_id : str,db : database_dependency, user : user_dependency, request : Request):
    await delete(db, user, public_id)


@router.get("/audit-logs")
async def audit_logs(db : database_dependency, user : user_dependency, request : Request):
    await get_audit_logs(db, user)

    
@router.post("/add-new-cultivation-type", status_code = status.HTTP_201_CREATED)
async def new_cultivation(db : database_dependency, user : user_dependency, cultivation_request : CultivationRequest, request : Request):
    await add_new_cultivation(db, user)

