import unittest
from unittest.mock import MagicMock

from src.controllers.peca_controller import PecaController
from src.models.peca_model import Peca


class TestPecaController(unittest.TestCase):

    def setUp(self):
        self.servico = MagicMock()
        self.controller = PecaController(self.servico)
        self.dados = {"referencia": "REF1", "nome": "Filtro", "preco_compra": "5,5",
                      "preco_venda": "9", "stock_atual": "3", "stock_minimo": "1",
                      "fornecedor": "Forn"}

    def test_listar_obter_e_eliminar_chamam_o_servico(self):
        self.controller.listar(True)
        self.controller.obter(4)
        self.controller.eliminar(4)

        self.servico.listar.assert_called_once_with(True)
        self.servico.obter.assert_called_once_with(4)
        self.servico.eliminar.assert_called_once_with(4)

    def test_guardar_converte_os_dados(self):
        self.controller.guardar(self.dados, 4)

        enviada = self.servico.guardar.call_args[0][0]
        self.assertEqual(enviada.referencia, "REF1")
        self.assertEqual(enviada.preco_compra, 5.5)
        self.assertEqual(enviada.preco_venda, 9.0)
        self.assertEqual(enviada.stock_atual, 3)
        self.assertEqual(enviada.stock_minimo, 1)
        self.assertEqual(enviada.id_peca, 4)

    def test_guardar_devolve_o_que_o_servico_devolve(self):
        esperada = Peca("REF1", "Filtro", 5.5, 9.0, 3, 1, "Forn", 4)
        self.servico.guardar.return_value = esperada

        self.assertIs(self.controller.guardar(self.dados), esperada)

    def test_guardar_rejeita_numeros_invalidos(self):
        for campo in ("preco_compra", "preco_venda", "stock_atual", "stock_minimo"):
            with self.subTest(campo=campo):
                dados = dict(self.dados)
                dados[campo] = "abc"

                with self.assertRaises(ValueError):
                    self.controller.guardar(dados)

                self.servico.guardar.assert_not_called()

    def test_ajustar_stock_converte_a_variacao(self):
        self.controller.ajustar_stock(4, "-3")

        self.servico.ajustar_stock.assert_called_once_with(4, -3)

    def test_ajustar_stock_rejeita_texto(self):
        with self.assertRaises(ValueError):
            self.controller.ajustar_stock(4, "muito")

        self.servico.ajustar_stock.assert_not_called()

    def test_receber_stock_converte_os_valores(self):
        self.controller.receber_stock(4, "10", "Forn", "6,5")

        self.servico.receber_stock.assert_called_once_with(4, 10, "Forn", 6.5)

    def test_receber_stock_rejeita_quantidade_invalida(self):
        with self.assertRaises(ValueError):
            self.controller.receber_stock(4, "dez", "Forn", "6,5")

        self.servico.receber_stock.assert_not_called()
