from sqlalchemy.ext.asyncio import AsyncSession


async def create_device(user_request, db : AsyncSession, user):
    pass

async def update_device_information(user_request, public_device_ip, db : AsyncSession, user):
    pass

async def update_device_key(public_device_ip, db : AsyncSession, user):
    pass

async def change_token_activity(public_device_ip, db : AsyncSession, user):
    pass

async def delete(user_request, db : AsyncSession, user):
    pass

async def all_user_device(db : AsyncSession, user):
    pass

async def user_specify_device(public_device_ip, db : AsyncSession, user):
    pass