
import unittest
from unittest.mock import Mock

from src.controllers.log_alteracao_ot_controller import (
    LogAlteracaoOTController
)
from auth import criar_token


class TestLogAlteracaoOTController(unittest.TestCase):

    def setUp(self):
        self.service = Mock()
        self.view = Mock()

        token = criar_token("teste", "administrador")

        self.controller = LogAlteracaoOTController(
            self.service,
            self.view,
            token
        )

    def test_consultar_alteracao(self):
        self.view.pedir_id_log.return_value = 1
        self.service.consultar_alteracao.return_value = Mock()

        self.controller.consultar_alteracao()

        self.service.consultar_alteracao.assert_called_once_with(1)
        self.view.mostrar_alteracao.assert_called_once()

    def test_consultar_alteracao_cancelada(self):
        self.view.pedir_id_log.return_value = None

        self.controller.consultar_alteracao()

        self.service.consultar_alteracao.assert_not_called()

    def test_listar_alteracoes_por_ot(self):
        self.view.pedir_id_ot.return_value = 1
        self.service.listar_alteracoes_por_ot.return_value = [Mock()]

        self.controller.listar_alteracoes_por_ot()

        self.service.listar_alteracoes_por_ot.assert_called_once_with(1)
        self.view.mostrar_alteracoes.assert_called_once()

    def test_listar_alteracoes_por_ot_cancelada(self):
        self.view.pedir_id_ot.return_value = None

        self.controller.listar_alteracoes_por_ot()

        self.service.listar_alteracoes_por_ot.assert_not_called()

    def test_listar_todas_alteracoes(self):
        self.service.listar_todas_alteracoes.return_value = [Mock()]

        self.controller.listar_todas_alteracoes()

        self.service.listar_todas_alteracoes.assert_called_once()
        self.view.mostrar_alteracoes.assert_called_once()

    def test_menu_abre_a_janela_do_menu_passando_o_controller(self):
        self.controller.menu()

        self.view.menu_log.assert_called_once_with(self.controller)
