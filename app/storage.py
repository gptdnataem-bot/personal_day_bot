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
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER,
                query TEXT,
                PRIMARY KEY (user_id, query)
            )
            '''
        )
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS sent (
                user_id INTEGER,
                url_hash TEXT,
                PRIMARY KEY (user_id, url_hash)
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

def add_subscription(user_id:int, query:str):
    query = (query or "").strip()
    if not query: return False
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO subscriptions (user_id, query) VALUES (?,?)", (user_id, query))
        con.commit()
    return True

def remove_subscription(user_id:int, query:str):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM subscriptions WHERE user_id=? AND query=?", (user_id, query))
        con.commit()

def list_subscriptions(user_id:int):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT query FROM subscriptions WHERE user_id=?", (user_id,))
        rows = cur.fetchall()
    return [r[0] for r in rows]

def mark_sent(user_id:int, url_hash:str):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO sent (user_id, url_hash) VALUES (?,?)", (user_id, url_hash))
        con.commit()

def was_sent(user_id:int, url_hash:str)->bool:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT 1 FROM sent WHERE user_id=? AND url_hash=?", (user_id, url_hash))
        row = cur.fetchone()
    return row is not None
