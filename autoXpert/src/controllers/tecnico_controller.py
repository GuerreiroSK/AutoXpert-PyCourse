from src.controllers.conversoes import ler_decimal
from src.models.tecnico_model import Tecnico


class TecnicoController:
    # Converte o texto do formulário em dados para o service.

    def __init__(self, servico):
        self.servico = servico

    def listar(self, apenas_ativos=False):
        return self.servico.listar(apenas_ativos)

    def obter(self, id_tecnico):
        return self.servico.obter(id_tecnico)

    # dados é um dicionário com o texto dos campos: nome, especialidade, custo_hora
    def guardar(self, dados, ativo, id_tecnico=None):
        tecnico = Tecnico(
            nome=dados["nome"],
            especialidade=dados["especialidade"],
            custo_hora=ler_decimal(dados["custo_hora"], "Custo/hora"),
            ativo=ativo,
            id_tecnico=id_tecnico
        )
        return self.servico.guardar(tecnico)

    def eliminar(self, id_tecnico):
        self.servico.eliminar(id_tecnico)
