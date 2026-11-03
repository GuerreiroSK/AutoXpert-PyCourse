from src.controllers.conversoes import ler_decimal
from src.models.tecnico import Tecnico
from src.services.tecnico_service import TecnicoService


class TecnicoController:
    """Converte o texto do formulario em dados para o servico."""

    def __init__(self, servico: TecnicoService):
        self.servico = servico

    def listar(self, apenas_ativos: bool = False) -> list[Tecnico]:
        return self.servico.listar(apenas_ativos)

    def obter(self, id_tecnico: int) -> Tecnico:
        return self.servico.obter(id_tecnico)

    def guardar(
        self, dados: dict[str, str], ativo: bool, id_tecnico: int | None = None,
    ) -> Tecnico:
        tecnico = Tecnico(
            nome=dados["nome"],
            especialidade=dados["especialidade"],
            custo_hora=ler_decimal(dados["custo_hora"], "Custo/hora"),
            ativo=ativo,
            id_tecnico=id_tecnico,
        )
        return self.servico.guardar(tecnico)

    def eliminar(self, id_tecnico: int) -> None:
        self.servico.eliminar(id_tecnico)
