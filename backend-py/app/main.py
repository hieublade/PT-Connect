import logging
from contextlib import asynccontextmanager
from pathlib import Path
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pymysql

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="PT Connect Backend API",
    description="Backend API cho nền tảng kết nối Huấn luyện viên cá nhân PT Connect",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
Path("static/uploads").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/app/static", StaticFiles(directory="static"), name="app_static")
app.include_router(api_v1_router)
