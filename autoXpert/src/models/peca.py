from dataclasses import dataclass
import sqlite3


@dataclass
class Peca:
    """Representa uma peca e os seus dados de catalogo e stock."""

    referencia: str
    nome: str
    preco_compra: float
    preco_venda: float
    stock_atual: int = 0
    stock_minimo: int = 0
    fornecedor: str | None = None
    id_peca: int | None = None

    @property
    def stock_baixo(self) -> bool:
        return self.stock_atual <= self.stock_minimo

    @classmethod
    def da_linha(cls, linha: sqlite3.Row) -> "Peca":
        return cls(
            referencia=linha["referencia"],
            nome=linha["nome"],
            preco_compra=linha["preco_compra"],
            preco_venda=linha["preco_venda"],
            stock_atual=linha["stock_atual"],
            stock_minimo=linha["stock_minimo"],
            fornecedor=linha["fornecedor"],
            id_peca=linha["id_peca"],
        )
