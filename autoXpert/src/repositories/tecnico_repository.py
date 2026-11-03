from contextlib import closing
import sqlite3

from db.connection import get_connection


def criar_tecnico(nome: str, especialidade: str | None, custo_hora: float, ativo: bool = True) -> int:
    """Guarda um tecnico e devolve o identificador criado."""
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """INSERT INTO Tecnico (nome, especialidade, custo_hora, ativo)
                VALUES (?, ?, ?, ?)""",
                (nome, especialidade, custo_hora, int(ativo)),
            )
            return cursor.lastrowid


def listar_tecnicos(apenas_ativos: bool = False) -> list[sqlite3.Row]:
    consulta = "SELECT * FROM Tecnico"
    if apenas_ativos:
        consulta += " WHERE ativo = 1"
    with closing(get_connection()) as conn:
        return conn.execute(consulta + " ORDER BY nome, id_tecnico").fetchall()


def obter_tecnico(id_tecnico: int) -> sqlite3.Row | None:
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM Tecnico WHERE id_tecnico = ?", (id_tecnico,)
        ).fetchone()


def atualizar_tecnico(
    id_tecnico: int, nome: str, especialidade: str | None,
    custo_hora: float, ativo: bool,
) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """UPDATE Tecnico SET nome = ?, especialidade = ?,
                custo_hora = ?, ativo = ? WHERE id_tecnico = ?""",
                (nome, especialidade, custo_hora, int(ativo), id_tecnico),
            )
            return cursor.rowcount == 1


def eliminar_tecnico(id_tecnico: int) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                "DELETE FROM Tecnico WHERE id_tecnico = ?", (id_tecnico,)
            )
            return cursor.rowcount == 1