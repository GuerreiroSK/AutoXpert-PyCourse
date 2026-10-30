from contextlib import closing
from datetime import datetime
import sqlite3

from db.connection import get_connection


def registar_alteracao_ot(
    id_ot: int, campo_alterado: str, valor_anterior: str | None = None,
    valor_novo: str | None = None, data_hora: str | None = None,
) -> int:
    momento = data_hora or datetime.now().isoformat(sep=" ", timespec="seconds")
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """INSERT INTO LogAlteracaoOT
                (id_ot, data_hora, campo_alterado, valor_anterior, valor_novo)
                VALUES (?, ?, ?, ?, ?)""",
                (id_ot, momento, campo_alterado, valor_anterior, valor_novo),
            )
            return cursor.lastrowid


def listar_alteracoes_por_ot(id_ot: int) -> list[sqlite3.Row]:
    with closing(get_connection()) as conn:
        return conn.execute(
            """SELECT * FROM LogAlteracaoOT WHERE id_ot = ?
            ORDER BY data_hora, id_log""",
            (id_ot,),
        ).fetchall()


def obter_alteracao(id_log: int) -> sqlite3.Row | None:
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM LogAlteracaoOT WHERE id_log = ?", (id_log,)
        ).fetchone()