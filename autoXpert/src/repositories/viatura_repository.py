<<<<<<< HEAD
from contextlib import closing
import sqlite3

from db.connection import get_connection


def criar_viatura(
    matricula: str, marca: str, modelo: str, id_cliente: int,
    ano: int | None = None, cor: str | None = None, km_estrada: int = 0,
) -> int:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """INSERT INTO Viatura
                (matricula, marca, modelo, ano, cor, km_estrada, id_cliente)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (matricula, marca, modelo, ano, cor, km_estrada, id_cliente),
            )
            return cursor.lastrowid


def listar_viaturas() -> list[sqlite3.Row]:
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM Viatura ORDER BY matricula, id_viatura"
        ).fetchall()


def listar_viaturas_por_cliente(id_cliente: int) -> list[sqlite3.Row]:
    with closing(get_connection()) as conn:
        return conn.execute(
            """SELECT * FROM Viatura WHERE id_cliente = ?
            ORDER BY matricula, id_viatura""",
            (id_cliente,),
        ).fetchall()


def obter_viatura(id_viatura: int) -> sqlite3.Row | None:
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM Viatura WHERE id_viatura = ?", (id_viatura,)
        ).fetchone()


def obter_viatura_por_matricula(matricula: str) -> sqlite3.Row | None:
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM Viatura WHERE matricula = ?", (matricula,)
        ).fetchone()


def atualizar_viatura(
    id_viatura: int, matricula: str, marca: str, modelo: str,
    ano: int | None, cor: str | None, km_estrada: int, id_cliente: int,
) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """UPDATE Viatura SET matricula = ?, marca = ?, modelo = ?,
                ano = ?, cor = ?, km_estrada = ?, id_cliente = ?
                WHERE id_viatura = ?""",
                (matricula, marca, modelo, ano, cor, km_estrada, id_cliente, id_viatura),
            )
            return cursor.rowcount == 1


def listar_historico_ot(matricula: str) -> list[sqlite3.Row]:
    with closing(get_connection()) as conn:
        return conn.execute(
            """SELECT ot.* FROM OrdemTrabalho AS ot
            JOIN Viatura AS v ON v.id_viatura = ot.id_viatura
            WHERE v.matricula = ?
            ORDER BY ot.data_entrada DESC, ot.id_ot DESC""",
            (matricula,),
        ).fetchall()
=======

import sqlite3
from typing import Optional

from src.models.viatura import Viatura


class ViaturaRepository:

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def criar(self, viatura: Viatura) -> int:
        cursor = self.connection.execute(
            """
            INSERT INTO Viatura (
                matricula, marca, modelo, ano,
                cor, km_estrada, id_cliente
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                viatura.matricula,
                viatura.marca,
                viatura.modelo,
                viatura.ano,
                viatura.cor,
                viatura.km_estrada,
                viatura.id_cliente
            )
        )

        self.connection.commit()
        viatura.id_viatura = cursor.lastrowid
        return cursor.lastrowid

    def obter_por_id(self, id_viatura: int) -> Optional[Viatura]:
        cursor = self.connection.execute(
            "SELECT * FROM Viatura WHERE id_viatura = ?",
            (id_viatura,)
        )
        row = cursor.fetchone()

        return Viatura.from_row(row) if row else None

    def obter_por_matricula(
        self, matricula: str
    ) -> Optional[Viatura]:
        cursor = self.connection.execute(
            "SELECT * FROM Viatura WHERE matricula = ?",
            (matricula,)
        )
        row = cursor.fetchone()

        return Viatura.from_row(row) if row else None

    def listar_todas(self) -> list[Viatura]:
        cursor = self.connection.execute(
            "SELECT * FROM Viatura ORDER BY id_viatura"
        )
        return [Viatura.from_row(row) for row in cursor.fetchall()]

    def listar_por_cliente(self, id_cliente: int) -> list[Viatura]:
        cursor = self.connection.execute(
            """
            SELECT * FROM Viatura
            WHERE id_cliente = ?
            ORDER BY id_viatura
            """,
            (id_cliente,)
        )
        return [Viatura.from_row(row) for row in cursor.fetchall()]

    def atualizar(self, viatura: Viatura) -> bool:
        if viatura.id_viatura is None:
            return False

        cursor = self.connection.execute(
            """
            UPDATE Viatura
            SET matricula = ?, marca = ?, modelo = ?,
                ano = ?, cor = ?, km_estrada = ?,
                id_cliente = ?
            WHERE id_viatura = ?
            """,
            (
                viatura.matricula,
                viatura.marca,
                viatura.modelo,
                viatura.ano,
                viatura.cor,
                viatura.km_estrada,
                viatura.id_cliente,
                viatura.id_viatura
            )
        )

        self.connection.commit()
        return cursor.rowcount > 0

    def eliminar(self, id_viatura: int) -> bool:
        cursor = self.connection.execute(
            "DELETE FROM Viatura WHERE id_viatura = ?",
            (id_viatura,)
        )

        self.connection.commit()
        return cursor.rowcount > 0
>>>>>>> main
