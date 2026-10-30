import sqlite3

from src.models.linha_ot_model import LinhaOT
from src.controllers.ots_base_controller import OtsBaseController


class LinhaOTController(OtsBaseController):
    # Liga a view das linhas ao LinhaOTService. Não tem SQL nem regras de negócio
    # (isso é do service) e não mostra nada ao utilizador (isso é da view).
    #
    # Todos os métodos devolvem um par (ok, resultado):
    #   - se correu bem:   (True, resultado)       ex.: (True, <LinhaOT>)
    #   - se houve um erro: (False, "mensagem")    ex.: (False, "A quantidade tem de ser um número")

    MENSAGEM_FK = "A peça indicada não existe"

    def __init__(self, service):
        self.service = service

    # Os tipos possíveis de linha: "mao_obra" e "peca" (RF04)
    def lista_tipos_linha(self):
        return list(LinhaOT.TIPOS)

    def listar_linhas(self, id_ot):
        try:
            return True, self.service.listar_linhas(id_ot)
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)

    # RF04 + RF13: depois de adicionar, o service recalcula o custo da OT.
    # Aceita vírgula ou ponto nos números (40,5 ou 40.5).
    def adicionar_linha(self, id_ot, tipo, descricao, quantidade, preco_unitario,
                        horas_trabalhadas="", id_peca=""):
        try:
            linha = self.service.adicionar_linha(
                id_ot,
                self._texto_ou_none(tipo),
                descricao,
                self._para_decimal(quantidade, "A quantidade"),
                self._para_decimal(preco_unitario, "O preço unitário"),
                self._para_decimal(horas_trabalhadas, "As horas trabalhadas"),
                self._para_inteiro(id_peca, "A peça"))
            return True, linha
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)

    def remover_linha(self, id_linha):
        try:
            self.service.remover_linha(id_linha)
            return True, None
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)
