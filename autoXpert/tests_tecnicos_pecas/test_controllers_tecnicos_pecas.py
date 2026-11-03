import unittest
from unittest.mock import MagicMock

from src.controllers.peca_controller import PecaController
from src.controllers.tecnico_controller import TecnicoController
from src.models.peca import Peca
from src.models.tecnico import Tecnico


class TecnicoControllerTests(unittest.TestCase):
    def setUp(self):
        self.servico = MagicMock()
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

    def test_obter_devolve_tecnico_do_servico(self):
        # Arrange
        esperado = Tecnico("Ana", "Motor", 20.0, True, 8)
        self.servico.obter.return_value = esperado

        # Act
        resultado = self.controller.obter(8)

        # Assert
        self.servico.obter.assert_called_once_with(8)
        self.assertIs(resultado, esperado)

    def test_obter_propaga_erro_do_servico(self):
        self.servico.obter.side_effect = ValueError(
            "O tecnico selecionado ja nao existe."
        )

        with self.assertRaisesRegex(ValueError, "ja nao existe"):
            self.controller.obter(99)

        self.servico.obter.assert_called_once_with(99)

    def test_guardar_rejeita_varios_custos_invalidos(self):
        for custo in ["", "vinte", "20,5,0"]:
            with self.subTest(custo=custo):
                self.servico.reset_mock()
                dados = {
                    "nome": "Ana",
                    "especialidade": "Motor",
                    "custo_hora": custo,
                }

                with self.assertRaises(ValueError):
                    self.controller.guardar(dados, True)

                self.servico.guardar.assert_not_called()
                
class PecaControllerTests(unittest.TestCase):
    def setUp(self):
        self.servico = MagicMock()
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


    def test_ajustar_stock_devolve_peca_do_servico(self):
        esperado = Peca(
            "F1", "Filtro", 5.0, 10.0, 4, 1, None, 12
        )
        self.servico.ajustar_stock.return_value = esperado

        resultado = self.controller.ajustar_stock(12, "2")

        self.servico.ajustar_stock.assert_called_once_with(12, 2)
        self.assertIs(resultado, esperado)
    
    def test_ajustar_stock_rejeita_variacao_invalida(self):
        for variacao in ["", "duas", "1.5"]:
            with self.subTest(variacao=variacao):
                self.servico.reset_mock()

                with self.assertRaises(ValueError):
                    self.controller.ajustar_stock(12, variacao)

                self.servico.ajustar_stock.assert_not_called()
                
    def test_receber_stock_rejeita_preco_invalido(self):
        with self.assertRaises(ValueError):
            self.controller.receber_stock(
                12, "3", "Loja", "cinco"
            )

        self.servico.receber_stock.assert_not_called()
    def test_ajustar_stock_propaga_erro_do_servico(self):
        self.servico.ajustar_stock.side_effect = ValueError(
            "A saida pedida excede o stock disponivel."
        )

        with self.assertRaisesRegex(ValueError, "excede o stock"):
            self.controller.ajustar_stock(12, "-20")

        self.servico.ajustar_stock.assert_called_once_with(12, -20)
        
if __name__ == "__main__":
    unittest.main()
