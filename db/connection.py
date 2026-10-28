import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "autoxpert.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_bd():
    schema = Path(__file__).parent / "schema.sql"

    with get_connection() as conn:
        conn.executescript(schema.read_text(encoding="utf-8"))
