from sqlalchemy.ext.asyncio import AsyncSession
from database.models import AuditLog

async def create_audit_log(db : AsyncSession, user_id : int, action : str, entity_type : str, entity_id : str):
    log = AuditLog(user_id = user_id,
                   action = action,
                   entity_type = entity_type,
                   entity_id = entity_id)
    db.add(log)