import unittest

from src.models.peca_model import Peca


class TestPecaModel(unittest.TestCase):

    def test_valores_por_defeito(self):
        peca = Peca("REF1", "Filtro", 5.0, 9.0)

        self.assertEqual(peca.stock_atual, 0)
        self.assertEqual(peca.stock_minimo, 0)
        self.assertIsNone(peca.fornecedor)
        self.assertIsNone(peca.id_peca)

    def test_stock_baixo(self):
        # (stock atual, stock mínimo, esperado)
        casos = [(1, 2, True), (2, 2, True), (3, 2, False), (0, 0, True)]
        for atual, minimo, esperado in casos:
            with self.subTest(atual=atual, minimo=minimo):
                peca = Peca("REF1", "Filtro", 5.0, 9.0, atual, minimo)

                self.assertEqual(peca.stock_baixo(), esperado)
