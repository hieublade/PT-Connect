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


def split_sql_statements(sql: str) -> list[str]:
    """Proper SQL splitter that respects single/double quotes and comments."""
    statements = []
    current = []
    in_single = False
    in_double = False
    i = 0
    n = len(sql)
    while i < n:
        c = sql[i]
        if not in_single and not in_double:
            if c == '-' and i + 1 < n and sql[i + 1] == '-':
                end_nl = sql.find('\n', i)
                if end_nl == -1:
                    break
                current.append(sql[i:end_nl + 1])
                i = end_nl + 1
                continue
            if c == '/' and i + 1 < n and sql[i + 1] == '*':
                end_c = sql.find('*/', i + 2)
                if end_c == -1:
                    break
                current.append(sql[i:end_c + 2])
                i = end_c + 2
                continue
            if c == ';':
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 1
                continue
        if c == "'" and (i == 0 or sql[i - 1] != '\\'):
            if not in_double:
                in_single = not in_single
        elif c == '"' and (i == 0 or sql[i - 1] != '\\'):
            if not in_single:
                in_double = not in_double
        current.append(c)
        i += 1
    last = "".join(current).strip()
    if last:
        statements.append(last)
    return statements


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
        root = Path(__file__).resolve().parent.parent  # /app in docker
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
                    blocks = re.split(r'DELIMITER\s*(?:\$\$|//)', content)
                    for b in blocks:
                        for sb in re.split(r'(?:\$\$|//)', b):
                            stmt = sb.strip()
                            if stmt and not stmt.upper().startswith("DELIMITER"):
                                if "BEGIN" not in stmt.upper():
                                    for s in stmt.split(";"):
                                        s = s.strip()
                                        if s:
                                            try:
                                                cur.execute(s)
                                            except Exception:
                                                pass
                                else:
                                    try:
                                        cur.execute(stmt)
                                    except Exception as e:
                                        print("Trig err:", e)
                else:
                    stmts = split_sql_statements(content)
                    for s in stmts:
                        if s.upper().startswith("DELIMITER"):
                            continue
                        if "DELIMITER" in s:
                            continue
                        try:
                            cur.execute(s)
                        except Exception:
                            pass
                conn.commit()
            else:
                print(f"Could not find {fname} at any expected location!")

        cur.execute("SELECT COUNT(*) FROM bookings;")
        print(f"Aiven MySQL auto-seed complete! Total bookings: {cur.fetchone()[0]}")
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
