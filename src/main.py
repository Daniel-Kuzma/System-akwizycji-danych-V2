from fastapi import FastAPI
from starlette import status
from auth.controller import router as auth_router
from admin.controller import router as admin_router
from users.controller import router as users_router
from device.controller import router as device_router
from telemetry.controller import router as telemetry_router

app = FastAPI()

app.include_router(auth_router, tags = ["Authentication"]) 
app.include_router(users_router, tags = ["Users"], prefix = "/users") 
app.include_router(device_router, tags = ["Device"], prefix = "/device") 
app.include_router(telemetry_router, tags = ["Telemetry"], prefix = "/telemetry") 
app.include_router(admin_router, tags = ["Admin"], prefix = "/admin") 

@app.get("healthy-check", status_code = status.HTTP_200_OK)
async def healthy_check():
    return {"detail" : "Application is healthy"}