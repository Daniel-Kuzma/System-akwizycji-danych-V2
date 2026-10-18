# funkcje do endpoint
from fastapi import Depends, HTTPException
from starlette import status
from typing import Annotated
from core.settings import settings
from database.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from database.core import database_dependency
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from core.admin_logger import create_audit_log
from .schemas import CreateUserRequest

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"

crypt_context = CryptContext(schemes = ["argon2"], deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")
oauth2_password_request = Annotated[OAuth2PasswordRequestForm, Depends()]

async def authenticate_user(user : str, password : str, db : database_dependency):
    stm = await db.execute(select(User).where(User.username == user))
    user_responds = stm.scalar()
    if user_responds is None:
        return False
    if crypt_context.verify(password, user_responds.password) == False:
        return False 
    if not user_responds.is_active:
        return False
    return user_responds

async def create_jwt_token(username : str, public_id : str, private_id : str, role : str, expired_time : timedelta):
    payload = {"username" : username, "public_id" : public_id, "private_id" : private_id, "role" : role}
    time_to_expired = datetime.now(timezone.utc) + timedelta(minutes = expired_time)
    payload.update({"exp" : time_to_expired})
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)

async def get_current_user(token : Annotated[str, Depends(oauth2_scheme)]):
    try:
        user = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username : str = user.get("username")
        public_id : str = user.get("public_id")
        private_id : int = user.get("private_id")
        role : str = user.get("role")
        if username is None or public_id is None or role is None or private_id is None:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not valid user")
        return {"username" : username, "public_id" : public_id, "private_id" : private_id, "role" : role}
    except InvalidTokenError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not valid user")

user_dependency = Annotated[dict, Depends(get_current_user)]

async def create_user(request : CreateUserRequest, db : AsyncSession):
    user = User(
                name = request.name,
                lastname = request.lastname,
                username = request.username,
                password = crypt_context.hash(request.password),
                email = request.email
            )
    try:
        db.add(user)
        await db.flush()
        await create_audit_log(db, user_id = user.id, action = "CREATE ACCOUNT", entity_type = "user", entity_id = str(user.public_id))
        await db.commit()
        return {"message" : "Successfully created user account"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")


