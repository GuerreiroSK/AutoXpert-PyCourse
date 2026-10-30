
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogAlteracaoOT:
    id_ot: int
    data_hora: str
    campo_alterado: str
    id_log: Optional[int] = None
    valor_anterior: Optional[str] = None
    valor_novo: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        return cls(
            id_log=row["id_log"],
            id_ot=row["id_ot"],
            data_hora=row["data_hora"],
            campo_alterado=row["campo_alterado"],
            valor_anterior=row["valor_anterior"],
            valor_novo=row["valor_novo"]
        )

    def obter_resumo(self) -> str:
        return (
            f"OT {self.id_ot} | "
            f"Campo: {self.campo_alterado} | "
            f"Anterior: {self.valor_anterior} | "
            f"Novo: {self.valor_novo} | "
            f"Data: {self.data_hora}"
        )
