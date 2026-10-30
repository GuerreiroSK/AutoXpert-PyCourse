
import sqlite3
from datetime import datetime
from typing import Optional

from models.log_alteracao_ot import LogAlteracaoOT

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
