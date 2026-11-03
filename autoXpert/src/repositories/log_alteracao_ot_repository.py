<<<<<<< HEAD
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
=======

import sqlite3
from datetime import datetime
from typing import Optional

from src.models.log_alteracao_ot import LogAlteracaoOT

class LogAlteracaoOTRepository:

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def registar(
        self,
        log: LogAlteracaoOT
    ) -> int:
        if not log.data_hora:
            log.data_hora = datetime.now().isoformat(
                timespec="seconds"
            )

        cursor = self.connection.execute(
            """
            INSERT INTO LogAlteracaoOT (
                id_ot,
                data_hora,
                campo_alterado,
                valor_anterior,
                valor_novo
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                log.id_ot,
                log.data_hora,
                log.campo_alterado,
                log.valor_anterior,
                log.valor_novo
            )
        )

        self.connection.commit()
        log.id_log = cursor.lastrowid
        return cursor.lastrowid

    def obter_por_id(
        self, id_log: int
    ) -> Optional[LogAlteracaoOT]:
        cursor = self.connection.execute(
            "SELECT * FROM LogAlteracaoOT WHERE id_log = ?",
            (id_log,)
        )
        row = cursor.fetchone()

        return LogAlteracaoOT.from_row(row) if row else None

    def listar_por_ot(
        self, id_ot: int
    ) -> list[LogAlteracaoOT]:
        cursor = self.connection.execute(
            """
            SELECT * FROM LogAlteracaoOT
            WHERE id_ot = ?
            ORDER BY data_hora DESC, id_log DESC
            """,
            (id_ot,)
        )

        return [
            LogAlteracaoOT.from_row(row)
            for row in cursor.fetchall()
        ]

    def listar_todos(self) -> list[LogAlteracaoOT]:
        cursor = self.connection.execute(
            """
            SELECT * FROM LogAlteracaoOT
            ORDER BY data_hora DESC, id_log DESC
            """
        )

        return [
            LogAlteracaoOT.from_row(row)
            for row in cursor.fetchall()
        ]

    def eliminar(self, id_log: int) -> bool:
        cursor = self.connection.execute(
            "DELETE FROM LogAlteracaoOT WHERE id_log = ?",
            (id_log,)
        )

        self.connection.commit()
        return cursor.rowcount > 0
>>>>>>> main
