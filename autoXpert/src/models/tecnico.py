from dataclasses import dataclass
import sqlite3


@dataclass
class Tecnico:
    """Representa os dados de um tecnico, sem conhecer SQL nem a interface."""

    nome: str
    especialidade: str | None
    custo_hora: float
    ativo: bool = True
    id_tecnico: int | None = None

    @classmethod
    def da_linha(cls, linha: sqlite3.Row) -> "Tecnico":
        return cls(
            nome=linha["nome"],
            especialidade=linha["especialidade"],
            custo_hora=linha["custo_hora"],
            ativo=bool(linha["ativo"]),
            id_tecnico=linha["id_tecnico"],
        )
