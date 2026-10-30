
from dataclasses import dataclass
from typing import Optional


@dataclass
class Viatura:
    matricula: str
    marca: str
    modelo: str
    id_cliente: int
    id_viatura: Optional[int] = None
    ano: Optional[int] = None
    cor: Optional[str] = None
    km_estrada: int = 0

    @classmethod
    def from_row(cls, row):
        return cls(
            id_viatura=row["id_viatura"],
            matricula=row["matricula"],
            marca=row["marca"],
            modelo=row["modelo"],
            ano=row["ano"],
            cor=row["cor"],
            km_estrada=row["km_estrada"],
            id_cliente=row["id_cliente"]
        )

    def atualizar_dados(
        self,
        marca: str,
        modelo: str,
        ano: Optional[int],
        cor: Optional[str],
        km_estrada: int
    ):
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.cor = cor
        self.km_estrada = km_estrada
