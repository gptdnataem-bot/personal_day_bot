import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "bot.db"

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                city TEXT,
                tz TEXT DEFAULT 'Europe/Amsterdam',
                notify_hour INTEGER DEFAULT 9,
                notify_min INTEGER DEFAULT 0,
                currencies TEXT DEFAULT 'USD,EUR',
                topics TEXT DEFAULT 'world'
            )
            '''
        )
        con.commit()

def upsert_user(user_id: int):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        con.commit()

def set_user_settings(user_id:int, **kwargs):
    if not kwargs: 
        return
    keys = ", ".join([f"{k}=?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(f"UPDATE users SET {keys} WHERE user_id=?", values)
        con.commit()

def get_user(user_id:int):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT user_id, city, tz, notify_hour, notify_min, currencies, topics FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
    if not row:
        return None
    return {
        "user_id": row[0],
        "city": row[1],
        "tz": row[2],
        "notify_hour": row[3],
        "notify_min": row[4],
        "currencies": row[5],
        "topics": row[6],
    }

def all_users():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT user_id, city, tz, notify_hour, notify_min, currencies, topics FROM users")
        rows = cur.fetchall()
    users = []
    for r in rows:
        users.append({
            "user_id": r[0],
            "city": r[1],
            "tz": r[2],
            "notify_hour": r[3],
            "notify_min": r[4],
            "currencies": r[5],
            "topics": r[6],
        })
    return users
