from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import time

from config import UPLOAD_FOLDER
from routers.auth import auth_router
from routers.admin import admin_router
from routers.seller import seller_router
from routers.buyer import buyer_router

app = FastAPI()

# 1. Middleware lar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request(request: Request, call_next):
    print(f"Request: {request.method}, {request.url}")
    start_time = time.time()
    response = await call_next(request)
    print(f"Response: {response.status_code}. Time: {time.time() - start_time:.3f}s")
    return response

# 2. Static files
app.mount(f"/{UPLOAD_FOLDER}", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# 3. Routerlar
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(seller_router)
app.include_router(buyer_router)
