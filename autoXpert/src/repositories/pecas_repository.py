from contextlib import closing
import sqlite3

from db.connection import get_connection


def criar_peca(
    referencia: str, nome: str, preco_compra: float, preco_venda: float,
    stock_atual: int = 0, stock_minimo: int = 0, fornecedor: str | None = None,
) -> int:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """INSERT INTO Peca (referencia, nome, stock_atual, stock_minimo,
                preco_compra, preco_venda, fornecedor) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (referencia, nome, stock_atual, stock_minimo,
                 preco_compra, preco_venda, fornecedor),
            )
            return cursor.lastrowid


def listar_pecas() -> list[sqlite3.Row]:
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM Peca ORDER BY nome, id_peca").fetchall()


def obter_peca(id_peca: int) -> sqlite3.Row | None:
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM Peca WHERE id_peca = ?", (id_peca,)).fetchone()


def obter_peca_por_referencia(referencia: str) -> sqlite3.Row | None:
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM Peca WHERE referencia = ?", (referencia,)
        ).fetchone()


def listar_pecas_com_stock_baixo() -> list[sqlite3.Row]:
    with closing(get_connection()) as conn:
        return conn.execute(
            """SELECT * FROM Peca WHERE stock_atual <= stock_minimo
            ORDER BY nome, id_peca"""
        ).fetchall()


def atualizar_peca(
    id_peca: int, referencia: str, nome: str, stock_minimo: int,
    preco_compra: float, preco_venda: float, fornecedor: str | None,
) -> bool:
    """Altera o catalogo, sem substituir a quantidade em stock."""
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """UPDATE Peca SET referencia = ?, nome = ?, stock_minimo = ?,
                preco_compra = ?, preco_venda = ?, fornecedor = ? WHERE id_peca = ?""",
                (referencia, nome, stock_minimo, preco_compra, preco_venda,
                 fornecedor, id_peca),
            )
            return cursor.rowcount == 1


def atualizar_stock(id_peca: int, variacao: int) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                "UPDATE Peca SET stock_atual = stock_atual + ? WHERE id_peca = ?",
                (variacao, id_peca),
            )
            return cursor.rowcount == 1


def registar_entrada_stock(
    id_peca: int, quantidade: int, fornecedor: str, preco_compra: float,
) -> bool:
    if quantidade <= 0:
        raise ValueError("A quantidade recebida tem de ser superior a zero.")
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """UPDATE Peca SET stock_atual = stock_atual + ?,
                fornecedor = ?, preco_compra = ? WHERE id_peca = ?""",
                (quantidade, fornecedor, preco_compra, id_peca),
            )
            return cursor.rowcount == 1


def eliminar_peca(id_peca: int) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM Peca WHERE id_peca = ?", (id_peca,))
            return cursor.rowcount == 1