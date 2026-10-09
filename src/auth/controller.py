from fastapi import APIRouter, Request, HTTPException
from service import oauth2_password_request
from schemas import Token, CreateUserRequest
from service import create_jwt_token, authenticate_user, create_user
from starlette import status
from database.core import database_dependency

router = APIRouter()

@router.post("/token", response_model = Token)
async def login(request_token : oauth2_password_request, db : database_dependency, request : Request):
    login_user = await authenticate_user(request_token.username, request_token.password, db)
    if not login_user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Password or Username is incorrect")
    token = await create_jwt_token(login_user.username, str(login_user.public_id), login_user.role, 60)
    return {"access_token" : token, "token_type" : "bearer"}

@router.post("/create-account", status_code = status.HTTP_201_CREATED)
async def create_user_account(db : database_dependency, create_user_request : CreateUserRequest, request = Request):
    try:
        await create_user(create_user_request, db)
        return {"detail" : "Successfully create account"}
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))