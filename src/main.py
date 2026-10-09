from fastapi import FastAPI
from starlette import status
from auth import controller

app = FastAPI()

app.include_router(controller.router, tags = ["Authentication"]) # auth

@app.get("healthy-check", status_code = status.HTTP_200_OK)
async def healthy_check():
    return {"detail" : "Application is healthy"}