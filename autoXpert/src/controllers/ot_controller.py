import sqlite3

from src.models.ordem_trabalho_model import OrdemTrabalho
from src.controllers.ots_base_controller import OtsBaseController


class OrdemTrabalhoController(OtsBaseController):
    # Liga a view das OTs ao OrdemTrabalhoService. Não tem SQL nem regras de negócio
    # (isso é do service) e não mostra nada ao utilizador (isso é da view).
    # As linhas da OT têm o seu próprio controller (linha_ot_controller.py).
    #
    # O que faz:
    #   1. converte o que o utilizador escreveu (texto) para o tipo certo (int, None);
    #   2. chama o service;
    #   3. apanha os erros e devolve uma mensagem pronta a mostrar.
    #
    # Todos os métodos devolvem um par (ok, resultado):
    #   - se correu bem:   (True, resultado)       ex.: (True, <OrdemTrabalho>)
    #   - se houve um erro: (False, "mensagem")    ex.: (False, "Tem de indicar a viatura")

    MENSAGEM_FK = "A viatura ou o técnico indicados não existem"

    def __init__(self, service):
        self.service = service

    # Os estados possíveis de uma OT, pela ordem do fluxo (RF06)
    def lista_estados(self):
        return list(OrdemTrabalho.ESTADOS)

    # ---------- Ordens de trabalho ----------

    # RF03 + RF05
    def criar_ot(self, id_viatura, id_tecnico, data_entrada, data_prev_saida,
                 descricao_avaria):
        try:
            ot = self.service.criar_ot(
                self._para_inteiro(id_viatura, "A viatura"),
                self._para_inteiro(id_tecnico, "O técnico"),
                self._texto_ou_none(data_entrada),
                self._texto_ou_none(data_prev_saida),
                descricao_avaria)
            return True, ot
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)

    def obter_ot(self, id_ot):
        try:
            return True, self.service.obter_ot(id_ot)
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)

    # RF06: se o novo estado for "Entregue", a data de saída real pode vir vazia
    # (o service usa a data de hoje)
    def mudar_estado(self, id_ot, novo_estado, data_saida_real=""):
        try:
            ot = self.service.mudar_estado(
                id_ot, self._texto_ou_none(novo_estado),
                self._texto_ou_none(data_saida_real))
            return True, ot
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)

    # RF05
    def atribuir_tecnico(self, id_ot, id_tecnico):
        try:
            ot = self.service.atribuir_tecnico(
                id_ot, self._para_inteiro(id_tecnico, "O técnico"))
            return True, ot
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)

    # ---------- Listagens e pesquisas ----------

    # Todas as OTs, as mais recentes primeiro
    def listar_todas(self):
        try:
            return True, self.service.pesquisar_ots()
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)

    # RF14
    def listar_em_curso(self):
        try:
            return True, self.service.listar_em_curso()
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)

    # RF07
    def historico_por_matricula(self, matricula):
        try:
            return True, self.service.historico_por_matricula(matricula)
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)

    # RF12: os campos que vierem vazios são ignorados
    def pesquisar(self, data_inicio="", data_fim="", estado="", id_tecnico=""):
        try:
            ots = self.service.pesquisar_ots(
                self._texto_ou_none(data_inicio),
                self._texto_ou_none(data_fim),
                self._texto_ou_none(estado),
                self._para_inteiro(id_tecnico, "O técnico"))
            return True, ots
        except (ValueError, sqlite3.Error) as erro:
            return False, self._texto_do_erro(erro)
