from fastapi import FastAPI
from starlette import status
from auth.controller import router as auth_router
from admin.controller import router as admin_router
from users.controller import router as users_router
from device.controller import router as device_router
from telemetry.controller import router as telemetry_router
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import _rate_limit_exceeded_handler
from core.limiter import limiter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from contextlib import asynccontextmanager
from database.core import LocalAsyncSession
from core.schedules import change_device_status

async def check_device():
    async with LocalAsyncSession() as db:
        await change_device_status(db = db)

@asynccontextmanager
async def lifespan(app : FastAPI):
    executors = {
        'default': AsyncIOExecutor()
    }
    scheduler = AsyncIOScheduler(executors = executors)
    scheduler.add_job(check_device, "interval", minutes = 10, misfire_grace_time=600, coalesce=True)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan = lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router, tags = ["Authentication"]) 
app.include_router(users_router, tags = ["Users"], prefix = "/users") 
app.include_router(device_router, tags = ["Device"], prefix = "/device") 
app.include_router(telemetry_router, tags = ["Telemetry"], prefix = "/telemetry") 
app.include_router(admin_router, tags = ["Admin"], prefix = "/admin") 

@app.get("healthy-check", status_code = status.HTTP_200_OK)
async def healthy_check():
    return {"detail" : "Application is healthy"}