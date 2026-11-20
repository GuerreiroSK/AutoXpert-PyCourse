from contextlib import closing
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

    with closing(get_connection()) as conn:
        with conn:
            conn.executescript(schema.read_text(encoding="utf-8"))
            migrar_autor_log(conn)


def migrar_autor_log(conn):
    conn.execute("BEGIN IMMEDIATE")
    colunas = conn.execute("PRAGMA table_info(LogAlteracaoOT)").fetchall()
    if not any(coluna[1] == "autor" for coluna in colunas):
        conn.execute("ALTER TABLE LogAlteracaoOT ADD COLUMN autor TEXT")
