import unittest
from unittest.mock import Mock

from src.controllers.peca_controller import PecaController
from src.controllers.tecnico_controller import TecnicoController
from src.models.peca import Peca
from src.models.tecnico import Tecnico


class TecnicoControllerTests(unittest.TestCase):
    def setUp(self):
        self.servico = Mock()
        self.controller = TecnicoController(self.servico)

    def test_listar_obter_e_eliminar_chamam_o_servico(self):
        self.controller.listar(True)
        self.controller.obter(8)
        self.controller.eliminar(8)

        self.servico.listar.assert_called_once_with(True)
        self.servico.obter.assert_called_once_with(8)
        self.servico.eliminar.assert_called_once_with(8)

    def test_guardar_converte_dados_e_chama_o_servico(self):
        dados = {
            "nome": "Ana",
            "especialidade": "Motor",
            "custo_hora": "20,50",
        }

        self.controller.guardar(dados, False, 8)

        self.servico.guardar.assert_called_once_with(
            Tecnico("Ana", "Motor", 20.5, False, 8)
        )

    def test_guardar_rejeita_custo_hora_invalido(self):
        dados = {
            "nome": "Ana",
            "especialidade": "Motor",
            "custo_hora": "vinte",
        }

        with self.assertRaises(ValueError):
            self.controller.guardar(dados, True)

        self.servico.guardar.assert_not_called()


class PecaControllerTests(unittest.TestCase):
    def setUp(self):
        self.servico = Mock()
        self.controller = PecaController(self.servico)

    def test_listar_obter_e_eliminar_chamam_o_servico(self):
        self.controller.listar(True)
        self.controller.obter(12)
        self.controller.eliminar(12)

        self.servico.listar.assert_called_once_with(True)
        self.servico.obter.assert_called_once_with(12)
        self.servico.eliminar.assert_called_once_with(12)

    def test_guardar_converte_dados_e_chama_o_servico(self):
        dados = {
            "referencia": "F1",
            "nome": "Filtro",
            "preco_compra": "5,25",
            "preco_venda": "10.50",
            "stock_atual": "3",
            "stock_minimo": "2",
            "fornecedor": "Loja",
        }

        self.controller.guardar(dados, 12)

        self.servico.guardar.assert_called_once_with(
            Peca("F1", "Filtro", 5.25, 10.5, 3, 2, "Loja", 12)
        )

    def test_guardar_rejeita_preco_invalido(self):
        dados = {
            "referencia": "F1",
            "nome": "Filtro",
            "preco_compra": "cinco",
            "preco_venda": "10",
            "stock_atual": "3",
            "stock_minimo": "2",
            "fornecedor": "Loja",
        }

        with self.assertRaises(ValueError):
            self.controller.guardar(dados)

        self.servico.guardar.assert_not_called()

    def test_guardar_rejeita_stock_que_nao_seja_inteiro(self):
        dados = {
            "referencia": "F1",
            "nome": "Filtro",
            "preco_compra": "5",
            "preco_venda": "10",
            "stock_atual": "1.5",
            "stock_minimo": "2",
            "fornecedor": "Loja",
        }

        with self.assertRaises(ValueError):
            self.controller.guardar(dados)

        self.servico.guardar.assert_not_called()

    def test_ajustar_stock_converte_variacao(self):
        self.controller.ajustar_stock(12, "-2")

        self.servico.ajustar_stock.assert_called_once_with(12, -2)

    def test_receber_stock_converte_quantidade_e_preco(self):
        self.controller.receber_stock(12, "3", "Loja", "5,25")

        self.servico.receber_stock.assert_called_once_with(12, 3, "Loja", 5.25)

    def test_receber_stock_rejeita_quantidade_invalida(self):
        with self.assertRaises(ValueError):
            self.controller.receber_stock(12, "duas", "Loja", "5,25")

        self.servico.receber_stock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
