from contextlib import closing
import sqlite3
import unittest

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
        self.assertTrue(Peca("F1", "Filtro", 5, 10, 2, 2).stock_baixo)
        self.assertFalse(Peca("F1", "Filtro", 5, 10, 3, 2).stock_baixo)

    def test_peca_e_criada_a_partir_de_linha_sqlite(self):
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute(
                """CREATE TABLE Peca (
                referencia TEXT, nome TEXT, preco_compra REAL, preco_venda REAL,
                stock_atual INTEGER, stock_minimo INTEGER, fornecedor TEXT, id_peca INTEGER
                )"""
            )
            conn.execute(
                "INSERT INTO Peca VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ("F1", "Filtro", 5.0, 10.0, 2, 1, "Loja", 7),
            )
            linha = conn.execute("SELECT * FROM Peca").fetchone()

        self.assertEqual(
            Peca.da_linha(linha), Peca("F1", "Filtro", 5.0, 10.0, 2, 1, "Loja", 7)
        )

    def test_tecnico_tem_valores_padrao(self):
        tecnico = Tecnico("Ana", None, 20.0)

        self.assertTrue(tecnico.ativo)
        self.assertIsNone(tecnico.id_tecnico)

    def test_tecnico_e_criado_a_partir_de_linha_sqlite(self):
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute(
                """CREATE TABLE Tecnico (
                nome TEXT, especialidade TEXT, custo_hora REAL, ativo INTEGER, id_tecnico INTEGER
                )"""
            )
            conn.execute(
                "INSERT INTO Tecnico VALUES (?, ?, ?, ?, ?)",
                ("Ana", "Motor", 20.0, 0, 9),
            )
            linha = conn.execute("SELECT * FROM Tecnico").fetchone()

        tecnico = Tecnico.da_linha(linha)

        self.assertEqual(tecnico, Tecnico("Ana", "Motor", 20.0, False, 9))
        self.assertIsInstance(tecnico.ativo, bool)
