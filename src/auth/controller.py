from fastapi import APIRouter, Request, HTTPException
from .service import oauth2_password_request
from .schemas import Token, CreateUserRequest, SuccessfulRespond
from .service import create_jwt_token, authenticate_user, create_user
from starlette import status
from database.core import database_dependency
from core.limiter import limiter
router = APIRouter()

@router.post("/token", response_model = Token)
@limiter.limit("8/minute")
async def login(request_token : oauth2_password_request, db : database_dependency, request : Request):
    login_user = await authenticate_user(request_token.username, request_token.password, db)
    if not login_user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Password or Username is incorrect")
    token = await create_jwt_token(login_user.username, str(login_user.public_id), login_user.id, login_user.user_role, 60)
    return {"access_token" : token, "token_type" : "bearer"}

@router.post("/create-account",  response_model = SuccessfulRespond, status_code = status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def create_user_account(db : database_dependency, create_user_request : CreateUserRequest, request : Request):
    return await create_user(create_user_request, db)
