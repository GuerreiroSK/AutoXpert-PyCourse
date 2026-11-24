from src.controllers.conversoes import ler_decimal
from src.models.tecnico_model import Tecnico
from src.rbac import require_perfil


class TecnicoController:
    # Converte o texto do formulário em dados para o service.

    def __init__(self, servico, token=None):
        self.servico = servico
        self.token = token

    @require_perfil("administrador")
    def listar(self, apenas_ativos=False):
        return self.servico.listar(apenas_ativos)

    @require_perfil("administrador")
    def obter(self, id_tecnico):
        return self.servico.obter(id_tecnico)

    # dados é um dicionário com o texto dos campos:
    # nome, especialidade, custo_hora
    @require_perfil("administrador")
    def guardar(self, dados, ativo, id_tecnico=None):
        tecnico = Tecnico(
            nome=dados["nome"],
            especialidade=dados["especialidade"],
            custo_hora=ler_decimal(dados["custo_hora"], "Custo/hora"),
            ativo=ativo,
            id_tecnico=id_tecnico
        )
        return self.servico.guardar(tecnico)

    @require_perfil("administrador")
    def eliminar(self, id_tecnico):
        self.servico.eliminar(id_tecnico)
