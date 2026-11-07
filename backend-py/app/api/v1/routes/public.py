from fastapi import APIRouter
from pathlib import Path
import re
import pymysql
from app.core.config import settings

router = APIRouter(prefix="/public", tags=["Public"])

@router.get("/health")
def health_check():
    return {"status": "UP", "message": "PT-Connect Backend is healthy"}

@router.get("/init-db-now")
def init_db_now():
    logs = []
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
        root = Path(__file__).resolve().parents[4] # try root
        candidates = [
            root / "database",
            Path("/app/database"),
            Path("/app/backend-py/database"),
            Path("database")
        ]
        db_dir = None
        for c in candidates:
            if (c / "init.sql").exists():
                db_dir = c
                break
        
        if not db_dir:
            return {"status": "error", "message": "SQL files not found", "checked": [str(c) for c in candidates]}

        for fname in ["init.sql", "trigger.sql", "seed_demo.sql"]:
            fpath = db_dir / fname
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
                            except Exception as e: logs.append(f"trig: {e}")
            else:
                for s in content.split(";"):
                    stmt = s.strip()
                    if stmt:
                        try: cur.execute(stmt)
                        except Exception as e: logs.append(f"stmt: {e}")
            conn.commit()
        
        cur.execute("SELECT COUNT(*) FROM users;")
        user_cnt = cur.fetchone()[0]
        conn.close()
        return {"status": "success", "users_count": user_cnt, "logs_count": len(logs)}
    except Exception as e:
        return {"status": "error", "exception": str(e), "logs": logs}
