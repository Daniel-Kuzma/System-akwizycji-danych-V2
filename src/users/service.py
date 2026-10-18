from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from starlette import status
from .schemas import PasswordRequest, ChangeInformationRequest, ChangePasswordRequest
from sqlalchemy import select, update, delete
from database.models import User
from sqlalchemy.orm import load_only
from auth.service import crypt_context
from password_generator import PasswordGenerator
from core.admin_logger import create_audit_log

async def instruction():
    return {"message" : "soon"}

async def get_user_information(db : AsyncSession, user):
    user_information_stmt = await db.execute(select(User)
                                             .where(User.id == user.get("private_id"))
                                             .options(load_only(User.name,
                                                                User.lastname,
                                                                User.username,
                                                                User.email,
                                                                User.public_id,
                                                                User.created_at)).limit(1))
    user_information_result = user_information_stmt.scalar()
    try: 
        return user_information_result
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def update_user_information(user_request : ChangeInformationRequest, db : AsyncSession, user):
    try: 
        await db.execute(update(User).values(name = user_request.name,
                                            lastname = user_request.lastname,
                                            username = user_request.username, 
                                            email =  user_request.email)
                                            .where(User.id == user.get("private_id")))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE USER INFORMATION", entity_type = "user", entity_id = user.get("public_id"))
        await db.commit()
        return {"message" : "Successfully changed account information"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def update_user_password(user_request : ChangePasswordRequest, db : AsyncSession, user):
    user_password_stmt = await db.execute(select(User.password).where(User.id == user.get("private_id")).limit(1))
    user_password_result = user_password_stmt.scalar()

    if not crypt_context.verify(user_request.old_password, user_password_result):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "You provide wrong password. Try again")
    
    new_password = crypt_context.hash(user_request.new_password)
    
    try: 
        await db.execute(update(User).values(password = new_password).where(User.id == user.get("private_id")))
        await create_audit_log(db, user_id = user.get("private_id"), action = "UPDATE USER PASSWORD", entity_type = "user", entity_id = user.get("public_id"))
        await db.commit()
        return {"message" : "Successfully changed password"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def delete_user(user_request : PasswordRequest, db : AsyncSession, user):
        user_password_stmt = await db.execute(select(User.password).where(User.id == user.get("private_id")).limit(1))
        user_password_result = user_password_stmt.scalar()
        if not crypt_context.verify(user_request.password, user_password_result):
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "You provide wrong password. Try again")
        try:
            await create_audit_log(db, user_id = user.get("private_id"), action = "DELETE USER ACCOUNT", entity_type = "user", entity_id = user.get("public_id"))
            await db.execute(delete(User).where(User.id == user.get("private_id")))
            await db.commit()
            return {"message" : "Successfully deleted account"}
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")

async def reset_password(db : AsyncSession, user):
    password_generator = PasswordGenerator()
    random_password = password_generator.generate()
    try:
        await db.execute(update(User).where(User.id == user.get("private_id")).values(password = crypt_context.hash(random_password)))
        await create_audit_log(db, user_id = user.get("private_id"), action = "RESET USER PASSWORD", entity_type = "user", entity_id = user.get("public_id"))
        await db.commit()
        return {"message" : f"New user password: {random_password}, login with new password and change this password"}
        # tu pewnie bedzie dodane wysyłanie maila z nowym hasłem
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Critical problem with server:")