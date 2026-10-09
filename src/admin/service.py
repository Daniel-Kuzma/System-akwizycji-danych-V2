from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User

async def get_all_users(db : AsyncSession, user):
    pass

async def update_user_status(db : AsyncSession, user, public_id):
    pass

async def update_user_role(db : AsyncSession, user, public_id):
    pass

async def delete(db : AsyncSession, user, public_id):
    pass

async def get_audit_logs(db : AsyncSession, user):
    pass

async def add_new_cultivation(db : AsyncSession, user, request):
    pass

