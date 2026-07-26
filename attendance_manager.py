import sqlite3
from datetime import datetime, date
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "attendance.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Present',
            UNIQUE(name, date)
        )
    """)
    conn.commit()
    conn.close()


def mark_attendance(name: str) -> tuple[bool, str]:
    """Returns (success, message)"""
    init_db()
    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO attendance (name, date, time, status) VALUES (?, ?, ?, ?)",
            (name, today, now, "Present")
        )
        conn.commit()
        return True, f"✅ Attendance marked for **{name}** at {now}"
    except sqlite3.IntegrityError:
        return False, f"⚠️ {name} already marked present today"
    finally:
        conn.close()


def get_attendance(date_filter: str = None) -> pd.DataFrame:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    if date_filter:
        df = pd.read_sql_query(
            "SELECT name, date, time, status FROM attendance WHERE date = ? ORDER BY time DESC",
            conn, params=(date_filter,)
        )
    else:
        df = pd.read_sql_query(
            "SELECT name, date, time, status FROM attendance ORDER BY date DESC, time DESC",
            conn
        )
    conn.close()
    return df


def get_today_attendance() -> pd.DataFrame:
    return get_attendance(date.today().isoformat())


def delete_attendance_record(name: str, record_date: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE name = ? AND date = ?", (name, record_date))
    conn.commit()
    conn.close()