import os, sys, re
import pymysql

print("Running automatic DB schema migration on startup...")
HOST = os.getenv("DB_HOST", "127.0.0.1")
PORT = int(os.getenv("DB_PORT", 3306))
USER = os.getenv("DB_USER", "root")
PASSWORD = os.getenv("DB_PASSWORD", "")
DATABASE = os.getenv("DB_NAME", "ptconnect")

try:
    conn = pymysql.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        charset="utf8mb4",
        ssl={"check_hostname": False},
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'users';")
    if not cursor.fetchone():
        print("Tables not found. Initializing schema and demo data on Aiven...")
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        
        for sql_file in [root / "database" / "init.sql", root / "database" / "trigger.sql", root / "database" / "seed_demo.sql"]:
            if sql_file.exists():
                print(f"Executing {sql_file.name}...")
                content = sql_file.read_text(encoding="utf-8")
                content = re.sub(r'USE\s+[`]?ptconnect[`]?;', f'USE `{DATABASE}`;', content, flags=re.IGNORECASE)
                if "trigger" in sql_file.name:
                    blocks = re.split(r'DELIMITER\s+//', content)
                    for b in blocks:
                        sub_blocks = re.split(r'//\s+DELIMITER\s+;', b)
                        for sb in sub_blocks:
                            stmt = sb.strip()
                            if stmt and not stmt.startswith("DELIMITER"):
                                try:
                                    cursor.execute(stmt)
                                except Exception as e:
                                    pass
                else:
                    for s in content.split(";"):
                        stmt = s.strip()
                        if stmt:
                            try:
                                cursor.execute(stmt)
                            except Exception as e:
                                pass
                conn.commit()
        print("Schema and seed data applied successfully!")
    else:
        print("Database tables already exist. Skipping seed.")
    conn.close()
except Exception as e:
    print("Database init warning:", e)
