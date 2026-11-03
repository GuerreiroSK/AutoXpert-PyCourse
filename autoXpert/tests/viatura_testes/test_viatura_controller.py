
import unittest
from unittest.mock import Mock

from src.controllers.viatura_controller import ViaturaController
from src.models.viatura_model import Viatura


class TestViaturaController(unittest.TestCase):

    def setUp(self):
        self.service = Mock()
        self.view = Mock()

        self.controller = ViaturaController(
            self.service,
            self.view
        )

    def criar_viatura(self):
        return Viatura(
            matricula="AA-00-BB",
            marca="BMW",
            modelo="Série 1",
            id_cliente=1,
            ano=2022,
            cor="Preto",
            km_estrada=10000
        )

    def test_registar_viatura(self):
        self.view.pedir_dados_viatura.return_value = {
            "matricula": "AA-00-BB",
            "marca": "BMW",
            "modelo": "Série 1",
            "id_cliente": 1,
            "ano": 2022,
            "cor": "Preto",
            "km_estrada": 10000
        }

        self.service.registar_viatura.return_value = 1

        self.controller.registar_viatura()

        self.service.registar_viatura.assert_called_once()
        self.view.mostrar_mensagem.assert_called()

    def test_registar_viatura_cancelada(self):
        self.view.pedir_dados_viatura.return_value = None

        self.controller.registar_viatura()

        self.service.registar_viatura.assert_not_called()

    def test_consultar_viatura(self):
        self.view.pedir_matricula.return_value = "AA-00-BB"
        self.service.consultar_por_matricula.return_value = (
            self.criar_viatura()
        )

        self.controller.consultar_viatura()

        self.service.consultar_por_matricula.assert_called_once_with(
            "AA-00-BB"
        )

        self.view.mostrar_viatura.assert_called_once()

    def test_consultar_viatura_cancelada(self):
        self.view.pedir_matricula.return_value = None

        self.controller.consultar_viatura()

        self.service.consultar_por_matricula.assert_not_called()

    def test_listar_viaturas(self):
        self.service.listar_viaturas.return_value = [
            self.criar_viatura()
        ]

        self.controller.listar_viaturas()

        self.view.mostrar_viaturas.assert_called_once()

    def test_atualizar_viatura_cancelada(self):
        self.view.pedir_id_viatura.return_value = None

        self.controller.atualizar_viatura()

        self.service.consultar_por_id.assert_not_called()

    def test_eliminar_viatura_cancelada(self):
        self.view.pedir_id_viatura.return_value = None

        self.controller.eliminar_viatura()

        self.service.eliminar_viatura.assert_not_called()

    def test_eliminar_viatura(self):
        self.view.pedir_id_viatura.return_value = 1
        self.view.confirmar_eliminacao.return_value = True
        self.service.eliminar_viatura.return_value = True

        self.controller.eliminar_viatura()

        self.service.eliminar_viatura.assert_called_once_with(1)

    def test_eliminar_viatura_sem_confirmacao(self):
        self.view.pedir_id_viatura.return_value = 1
        self.view.confirmar_eliminacao.return_value = False

        self.controller.eliminar_viatura()

        self.service.eliminar_viatura.assert_not_called()

    def test_consultar_historico_cancelado(self):
        self.view.pedir_matricula.return_value = None

        self.controller.consultar_historico()

        self.service.consultar_por_matricula.assert_not_called()

    def test_consultar_historico_pede_ao_service_pela_matricula(self):
        # O service procura o histórico pela matrícula (e não pelo ID da viatura)
        self.view.pedir_matricula.return_value = "AA-00-BB"
        self.service.consultar_por_matricula.return_value = self.criar_viatura()
        self.service.consultar_historico.return_value = [{"id_ot": 1}]

        self.controller.consultar_historico()

        self.service.consultar_historico.assert_called_once_with("AA-00-BB")
        self.view.mostrar_historico.assert_called_once_with([{"id_ot": 1}])

    def test_consultar_historico_de_viatura_inexistente(self):
        self.view.pedir_matricula.return_value = "ZZ-99-ZZ"
        self.service.consultar_por_matricula.return_value = None

        self.controller.consultar_historico()

        self.service.consultar_historico.assert_not_called()
        self.view.mostrar_erro.assert_called_once()

    def test_menu_abre_a_janela_do_menu_passando_o_controller(self):
        self.controller.menu()

        self.view.menu_viatura.assert_called_once_with(self.controller)
