import logging
from contextlib import asynccontextmanager
from pathlib import Path
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers

logger = logging.getLogger(__name__)

def auto_seed_aiven():
    try:
        conn = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset="utf8mb4",
            ssl={"check_hostname": False},
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
        )
        cur = conn.cursor()
        print("Checking tables on Aiven MySQL...")
        root = Path(__file__).resolve().parent.parent # /app in docker
        for fname in ["init.sql", "trigger.sql", "seed_demo.sql"]:
            # Check multiple possible locations in docker container
            fpath = root / "database" / fname
            if not fpath.exists():
                fpath = root.parent / "database" / fname
            if not fpath.exists():
                fpath = Path("/app/database") / fname
            if not fpath.exists():
                fpath = Path("/app/backend-py/database") / fname
                
            if fpath.exists():
                print(f"Executing found SQL: {fpath}...")
                content = fpath.read_text(encoding="utf-8")
                content = re.sub(r'USE\s+[`]?ptconnect[`]?;', f'USE `{settings.DB_NAME}`;', content, flags=re.IGNORECASE)
                if "trigger" in fname:
                    blocks = re.split(r'DELIMITER\s+//', content)
                    for b in blocks:
                        sub_blocks = re.split(r'//\s+DELIMITER\s+;', b)
                        for sb in sub_blocks:
                            stmt = sb.strip()
                            if stmt and not stmt.startswith("DELIMITER"):
                                try: cur.execute(stmt)
                                except Exception as e: print("Trig err:", e)
                else:
                    for s in content.split(";"):
                        stmt = s.strip()
                        if stmt:
                            try: cur.execute(stmt)
                            except Exception as e: pass
                conn.commit()
            else:
                print(f"Could not find {fname} at any expected location!")
        conn.close()
    except Exception as e:
        print("Auto-seed error:", e)

@asynccontextmanager
async def lifespan(app: FastAPI):
    auto_seed_aiven()
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
app.include_router(api_v1_router)
