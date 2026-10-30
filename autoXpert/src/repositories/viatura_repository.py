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