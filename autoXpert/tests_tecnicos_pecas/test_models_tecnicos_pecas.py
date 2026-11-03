import sqlite3
import unittest
from unittest.mock import MagicMock

from src.models.peca import Peca
from src.models.tecnico import Tecnico


class ModelTests(unittest.TestCase):
    def test_peca_tem_valores_padrao(self):
        peca = Peca("F1", "Filtro", 5.0, 10.0)

        self.assertEqual(peca.stock_atual, 0)
        self.assertEqual(peca.stock_minimo, 0)
        self.assertIsNone(peca.fornecedor)
        self.assertIsNone(peca.id_peca)

    def test_stock_baixo_compara_stock_com_minimo(self):
        casos = [
            (1, 2, True),
            (2, 2, True),
            (3, 2, False),
            (0, 0, True),
        ]

        for stock_atual, stock_minimo, esperado in casos:
            with self.subTest(
                stock_atual=stock_atual,
                stock_minimo=stock_minimo,
            ):
                peca = Peca(
                    "F1",
                    "Filtro",
                    5.0,
                    10.0,
                    stock_atual,
                    stock_minimo,
                )

                self.assertEqual(peca.stock_baixo, esperado)

    def test_peca_e_criada_a_partir_de_linha_simulada(self):
        # Arrange
        dados = {
            "referencia": "F1",
            "nome": "Filtro",
            "preco_compra": 5.0,
            "preco_venda": 10.0,
            "stock_atual": 2,
            "stock_minimo": 1,
            "fornecedor": "Loja",
            "id_peca": 7,
        }
        linha = MagicMock(spec=sqlite3.Row)
        linha.__getitem__.side_effect = dados.__getitem__

        # Act
        resultado = Peca.da_linha(linha)

        # Assert
        esperado = Peca(
            "F1", "Filtro", 5.0, 10.0, 2, 1, "Loja", 7
        )
        self.assertEqual(resultado, esperado)

    def test_tecnico_tem_valores_padrao(self):
        tecnico = Tecnico("Ana", None, 20.0)

        self.assertTrue(tecnico.ativo)
        self.assertIsNone(tecnico.id_tecnico)

    def test_tecnico_e_criado_a_partir_de_linha_simulada(self):
        casos = [
            (0, False),
            (1, True),
        ]

        for ativo_bd, ativo_esperado in casos:
            with self.subTest(ativo=ativo_bd):
                dados = {
                    "nome": "Ana",
                    "especialidade": "Motor",
                    "custo_hora": 20.0,
                    "ativo": ativo_bd,
                    "id_tecnico": 9,
                }
                linha = MagicMock(spec=sqlite3.Row)
                linha.__getitem__.side_effect = dados.__getitem__

                resultado = Tecnico.da_linha(linha)

                esperado = Tecnico(
                    "Ana", "Motor", 20.0, ativo_esperado, 9
                )
                self.assertEqual(resultado, esperado)
                self.assertIsInstance(resultado.ativo, bool)


if __name__ == "__main__":
    unittest.main()