import sys
from pathlib import Path
src_path = str(Path(__file__).resolve().parent.parent / "src")
sys.path.insert(0, src_path)

from auth.schemas import CreateUserRequest
from database.core import LocalAsyncSession
from pydantic import ValidationError
from core.server_logger import logger
from database.models import User
from core.admin_logger import create_audit_log
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.service import crypt_context
import asyncio

async def user_check(username, email, db : AsyncSession):    
    email_stmt = await db.execute(select(User).where(User.email == email).limit(1))
    email_result = email_stmt.scalar()
    if email_result:
        return False
    
    username_stmt = await db.execute(select(User).where(User.username == username).limit(1))
    username_result = username_stmt.scalar()
    if username_result:
        return False

    return True

async def create_super_user():
    async with LocalAsyncSession() as db:
        name = str(input("name : "))
        lastname = str(input("lastname : "))
        username = str(input("username : "))
        password = str(input("password : "))
        email = str(input("email : "))

        try:
            user = CreateUserRequest(name = name,
                                    lastname = lastname,
                                    username = username,
                                    password = password,
                                    email = email)

            new_user = User(name = user.name,
                            lastname = user.lastname,
                            username = user.username,
                            password = crypt_context.hash(user.password),
                            email = user.email,
                            user_role = "admin")
            
            input_check = await user_check(user.username, user.email, db)
            if not input_check:
                print("User with this username or email already exist")
                return 

            db.add(new_user)
            await db.flush()
            await create_audit_log(db, user_id = new_user.id, action = "CREATE ACCOUNT USING CREATESUPERUSER FUNCTION", entity_type = "user", entity_id = str(new_user.public_id))
            await db.commit()

            print("Successfully create your admin account")
        except ValidationError as e:
            await db.rollback()
            errors = e.errors()
            for error in errors:
                if error.get("loc")[0] == "password":
                    print("The password should be 12 characters long and contain uppercase and lowercase letters and numbers")
                elif error.get("loc")[0] == "email":
                    print("Invalid email or user with this email already exist")
                elif error.get("loc")[0] == "name":
                    print("Name is too short")
                elif error.get("loc")[0] == "lastname":
                    print("Lastname is too short")
                elif error.get("loc")[0] == "username":
                    print("Username is too short or user with this username already exist")

        except Exception as e:
            await db.rollback()
            logger.exception("Critical problem with database trying to add new user")
            print("Critical problem with database trying to add new user")
                
if __name__ == "__main__":
    asyncio.run(create_super_user())