from fastapi import APIRouter
from pathlib import Path
import re
import pymysql
from app.core.config import settings

router = APIRouter(prefix="/public", tags=["Public"])


def split_sql_statements(sql: str) -> list[str]:
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
        root = Path(__file__).resolve().parents[4]  # try root
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
                                    logs.append(f"trig: {e}")
            else:
                stmts = split_sql_statements(content)
                for s in stmts:
                    if s.upper().startswith("DELIMITER") or "DELIMITER" in s:
                        continue
                    try:
                        cur.execute(s)
                    except Exception as e:
                        pass
            conn.commit()

        cur.execute("SHOW TABLES;")
        tables = [r[0] for r in cur.fetchall()]

        counts = {}
        for t in ["users", "bookings", "pt_profiles", "courses", "enrollments"]:
            if t in tables:
                cur.execute(f"SELECT COUNT(*) FROM `{t}`;")
                counts[t] = cur.fetchone()[0]

        conn.close()
        return {"status": "success", "tables_count": len(tables), "tables": tables, "counts": counts}
    except Exception as e:
        return {"status": "error", "exception": str(e), "logs": logs}
