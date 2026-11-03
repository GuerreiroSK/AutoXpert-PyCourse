import sqlite3
import unittest

from src.models.peca_model import Peca
from src.repositories.peca_repository import PecaRepository
from tests.bd_testes.base_dados_teste import criar_conexao_vazia


class TestPecaRepository(unittest.TestCase):
    # Testes de integração: repositório + base de dados SQLite em memória.

    def setUp(self):
        self.conexao = criar_conexao_vazia()
        self.repo = PecaRepository(self.conexao)

    def tearDown(self):
        self.conexao.close()

    def nova_peca(self, referencia="REF1", nome="Filtro", stock=5, minimo=2):
        return self.repo.inserir(Peca(referencia, nome, 5.0, 9.0, stock, minimo, "Forn"))

    def test_inserir_preenche_o_id(self):
        self.assertEqual(self.nova_peca().id_peca, 1)

    def test_obter_por_id_devolve_os_dados_certos(self):
        self.nova_peca()

        peca = self.repo.obter_por_id(1)

        self.assertIsInstance(peca, Peca)
        self.assertEqual(peca.referencia, "REF1")
        self.assertEqual(peca.nome, "Filtro")
        self.assertEqual(peca.preco_compra, 5.0)
        self.assertEqual(peca.preco_venda, 9.0)
        self.assertEqual(peca.stock_atual, 5)
        self.assertEqual(peca.stock_minimo, 2)
        self.assertEqual(peca.fornecedor, "Forn")

    def test_obter_inexistente_devolve_none(self):
        self.assertIsNone(self.repo.obter_por_id(99))
        self.assertIsNone(self.repo.obter_por_referencia("XXX"))

    def test_obter_por_referencia(self):
        self.nova_peca("REF9", "Óleo")

        self.assertEqual(self.repo.obter_por_referencia("REF9").nome, "Óleo")

    def test_referencia_repetida_e_recusada(self):
        self.nova_peca("REF1")

        with self.assertRaises(sqlite3.IntegrityError):
            self.nova_peca("REF1", "Outro")

    def test_listar_todas_por_ordem_de_nome(self):
        self.nova_peca("R1", "Vela")
        self.nova_peca("R2", "Filtro")

        nomes = []
        for peca in self.repo.listar_todos():
            nomes.append(peca.nome)

        self.assertEqual(nomes, ["Filtro", "Vela"])

    def test_listar_stock_baixo(self):
        self.nova_peca("R1", "Vela", 10, 2)
        self.nova_peca("R2", "Filtro", 2, 2)

        baixas = self.repo.listar_stock_baixo()

        self.assertEqual(len(baixas), 1)
        self.assertEqual(baixas[0].nome, "Filtro")

    def test_atualizar_nao_mexe_no_stock_atual(self):
        peca = self.nova_peca(stock=5)
        peca.nome = "Filtro de óleo"
        peca.stock_atual = 999     # tem de ser ignorado

        self.assertTrue(self.repo.atualizar(peca))

        guardada = self.repo.obter_por_id(1)
        self.assertEqual(guardada.nome, "Filtro de óleo")
        self.assertEqual(guardada.stock_atual, 5)

    def test_atualizar_inexistente_devolve_false(self):
        self.assertFalse(self.repo.atualizar(Peca("R", "N", 1.0, 2.0, 0, 0, None, 99)))

    def test_atualizar_stock_soma_e_subtrai(self):
        self.nova_peca(stock=5)

        self.assertTrue(self.repo.atualizar_stock(1, 3))
        self.assertEqual(self.repo.obter_por_id(1).stock_atual, 8)
        self.assertTrue(self.repo.atualizar_stock(1, -8))
        self.assertEqual(self.repo.obter_por_id(1).stock_atual, 0)

    def test_stock_negativo_e_recusado_pela_base_de_dados(self):
        self.nova_peca(stock=1)

        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.atualizar_stock(1, -2)

    def test_atualizar_stock_inexistente_devolve_false(self):
        self.assertFalse(self.repo.atualizar_stock(99, 1))

    def test_registar_entrada_soma_e_guarda_fornecedor_e_preco(self):
        self.nova_peca(stock=5)

        self.assertTrue(self.repo.registar_entrada(1, 10, "Novo Forn", 6.5))

        peca = self.repo.obter_por_id(1)
        self.assertEqual(peca.stock_atual, 15)
        self.assertEqual(peca.fornecedor, "Novo Forn")
        self.assertEqual(peca.preco_compra, 6.5)

    def test_registar_entrada_quantidade_invalida(self):
        self.nova_peca()

        for quantidade in (0, -1):
            with self.subTest(quantidade=quantidade):
                with self.assertRaises(ValueError):
                    self.repo.registar_entrada(1, quantidade, "F", 1.0)

    def test_eliminar(self):
        self.nova_peca()

        self.assertTrue(self.repo.eliminar(1))
        self.assertIsNone(self.repo.obter_por_id(1))
        self.assertFalse(self.repo.eliminar(1))
