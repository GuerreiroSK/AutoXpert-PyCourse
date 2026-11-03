
from datetime import datetime

from src.models.log_alteracao_ot_model import LogAlteracaoOT


class LogAlteracaoOTService:
    # Regras do registo de alterações. Todo o SQL fica nos repositórios, que são
    # recebidos aqui: o do registo e o das OTs (para ver se a OT existe).

    def __init__(self, log_repository, ot_repository):
        self.log_repository = log_repository
        self.ot_repository = ot_repository

    def registar_alteracao(
        self,
        id_ot,
        campo_alterado,
        valor_anterior,
        valor_novo
    ):
        # Validar o ID da ordem de trabalho
        if id_ot <= 0:
            raise ValueError("ID da ordem de trabalho inválido.")

        # Validar o campo alterado
        if not campo_alterado or not campo_alterado.strip():
            raise ValueError("O campo alterado é obrigatório.")

        # Verificar se a ordem de trabalho existe
        if self.ot_repository.procurar_por_id(id_ot) is None:
            raise ValueError("A ordem de trabalho não existe.")

        # Criar o registo da alteração
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # O repositório espera um objeto LogAlteracaoOT (e não um dicionário)
        registo = LogAlteracaoOT(
            id_ot=id_ot,
            data_hora=data_hora,
            campo_alterado=campo_alterado.strip(),
            valor_anterior=valor_anterior,
            valor_novo=valor_novo
        )

        # O repositório preenche o id_log do registo
        self.log_repository.registar(registo)

        return registo

    def consultar_alteracao(self, id_log):
        if id_log <= 0:
            raise ValueError("ID do registo inválido.")

        registo = self.log_repository.obter_por_id(id_log)

        if registo is None:
            raise ValueError("Registo de alteração não encontrado.")

        return registo

    def listar_alteracoes_por_ot(self, id_ot):
        if id_ot <= 0:
            raise ValueError("ID da ordem de trabalho inválido.")

        if self.ot_repository.procurar_por_id(id_ot) is None:
            raise ValueError("A ordem de trabalho não existe.")

        return self.log_repository.listar_por_ot(id_ot)

    def listar_todas_alteracoes(self):
        return self.log_repository.listar_todos()
