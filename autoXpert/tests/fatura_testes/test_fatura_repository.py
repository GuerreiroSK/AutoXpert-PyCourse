import sqlite3
import unittest

from src.models.fatura_model import Fatura
from src.repositories.fatura_repository import FaturaRepository
from tests.bd_testes.base_dados_teste import criar_conexao_teste


class TestFaturaRepository(unittest.TestCase):
    # Testes de integração: repositório + base de dados SQLite em memória.

    def setUp(self):
        self.conexao = criar_conexao_teste()
        for descricao in ("Avaria 1", "Avaria 2"):
            self.conexao.execute(
                "INSERT INTO OrdemTrabalho (id_viatura, id_tecnico, data_entrada, "
                "data_prev_saida, estado, descricao_avaria) "
                "VALUES (1, 1, '2026-11-03', '2026-11-05', 'Concluída', ?)", (descricao,))
        self.conexao.commit()
        self.repo = FaturaRepository(self.conexao)

    def tearDown(self):
        self.conexao.close()

    def test_inserir_preenche_o_id(self):
        fatura = self.repo.inserir(Fatura(1, "2026-11-03", 100.0))

        self.assertEqual(fatura.id_fatura, 1)

    def test_obter_por_id_devolve_os_dados_certos(self):
        self.repo.inserir(Fatura(1, "2026-11-03", 100.5))

        fatura = self.repo.obter_por_id(1)

        self.assertIsInstance(fatura, Fatura)
        self.assertEqual(fatura.id_ot, 1)
        self.assertEqual(fatura.data_emissao, "2026-11-03")
        self.assertEqual(fatura.valor_total, 100.5)
        self.assertEqual(fatura.pago, 0)
        self.assertIsNone(fatura.data_pagamento)

    def test_obter_inexistente_devolve_none(self):
        self.assertIsNone(self.repo.obter_por_id(99))
        self.assertIsNone(self.repo.obter_por_ot(99))

    def test_obter_por_ot(self):
        self.repo.inserir(Fatura(2, "2026-11-03", 50.0))

        self.assertEqual(self.repo.obter_por_ot(2).id_fatura, 1)

    def test_so_pode_haver_uma_fatura_por_ot(self):
        self.repo.inserir(Fatura(1, "2026-11-03", 100.0))

        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.inserir(Fatura(1, "2026-11-04", 50.0))

    def test_listar_todos(self):
        self.repo.inserir(Fatura(1, "2026-11-03", 100.0))
        self.repo.inserir(Fatura(2, "2026-11-04", 50.0))

        self.assertEqual(len(self.repo.listar_todos()), 2)

    def test_atualizar(self):
        fatura = self.repo.inserir(Fatura(1, "2026-11-03", 100.0))
        fatura.valor_total = 120.0

        self.assertTrue(self.repo.atualizar(fatura))
        self.assertEqual(self.repo.obter_por_id(1).valor_total, 120.0)

    def test_atualizar_inexistente_devolve_false(self):
        self.assertFalse(self.repo.atualizar(Fatura(1, "2026-11-03", 1.0, 0, None, None, 99)))

    def test_marcar_como_paga(self):
        self.repo.inserir(Fatura(1, "2026-11-03", 100.0))

        self.assertTrue(self.repo.marcar_como_paga(1, "2026-11-10", "MB"))

        fatura = self.repo.obter_por_id(1)
        self.assertEqual(fatura.pago, 1)
        self.assertEqual(fatura.data_pagamento, "2026-11-10")
        self.assertEqual(fatura.metodo_pagamento, "MB")
        self.assertFalse(self.repo.marcar_como_paga(99, "2026-11-10", "MB"))

    def test_listar_por_mes(self):
        self.repo.inserir(Fatura(1, "2026-11-03", 100.0))
        self.repo.inserir(Fatura(2, "2026-03-15", 50.0))

        novembro = self.repo.listar_por_mes(11, 2026)
        marco = self.repo.listar_por_mes(3, 2026)

        self.assertEqual(len(novembro), 1)
        self.assertEqual(novembro[0].id_ot, 1)
        self.assertEqual(len(marco), 1)    # mês com um só algarismo
        self.assertEqual(self.repo.listar_por_mes(11, 2025), [])

    def test_obter_linhas_ot_devolve_dicionarios(self):
        self.conexao.execute(
            "INSERT INTO LinhaOT (id_ot, tipo, descricao, quantidade, horas_trabalhadas, "
            "preco_unitario) VALUES (1, 'mao_obra', 'Revisão', 1, 2, 25)")
        self.conexao.commit()

        linhas = self.repo.obter_linhas_ot(1)

        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["tipo"], "mao_obra")
        self.assertEqual(linhas[0]["preco_unitario"], 25)
        self.assertEqual(self.repo.obter_linhas_ot(2), [])

    def test_eliminar(self):
        self.repo.inserir(Fatura(1, "2026-11-03", 100.0))

        self.assertTrue(self.repo.eliminar(1))
        self.assertFalse(self.repo.eliminar(1))
