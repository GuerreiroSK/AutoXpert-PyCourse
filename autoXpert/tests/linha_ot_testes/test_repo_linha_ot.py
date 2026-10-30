import sqlite3
import unittest

from src.models.ordem_trabalho_model import OrdemTrabalho
from src.models.linha_ot_model import LinhaOT
from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.repositories.linha_ot_repository import LinhaOTRepository
from tests.bd_testes.base_dados_teste import criar_conexao_teste


class TesteLinhaOTRepository(unittest.TestCase):

    def setUp(self):
        self.conexao = criar_conexao_teste()
        self.repo_ot = OrdemTrabalhoRepository(self.conexao)
        self.repo = LinhaOTRepository(self.conexao)
        self.ot1 = self.repo_ot.inserir(
            OrdemTrabalho(1, 1, "2026-10-28", "2026-10-30", "OT 1"))
        self.ot2 = self.repo_ot.inserir(
            OrdemTrabalho(2, 2, "2026-10-29", "2026-10-31", "OT 2"))

    def tearDown(self):
        self.conexao.close()

    def _mao_obra(self, id_ot):
        return self.repo.inserir(
            LinhaOT(id_ot, LinhaOT.TIPO_MAO_OBRA, "Mão-de-obra", 1.5, 40.0,
                    horas_trabalhadas=1.5))

    def _peca(self, id_ot, id_peca=1):
        return self.repo.inserir(
            LinhaOT(id_ot, LinhaOT.TIPO_PECA, "Pastilhas", 2, 25.0, id_peca=id_peca))

    def test_inserir_preenche_o_id(self):
        self.assertEqual(self._mao_obra(self.ot1.id_ot).id_linha, 1)
        self.assertEqual(self._peca(self.ot1.id_ot).id_linha, 2)

    def test_procurar_por_id(self):
        linha = self._peca(self.ot1.id_ot)
        lida = self.repo.procurar_por_id(linha.id_linha)
        self.assertEqual(lida.descricao, "Pastilhas")
        self.assertEqual(lida.id_peca, 1)
        self.assertIsNone(lida.horas_trabalhadas)
        self.assertIsNone(self.repo.procurar_por_id(99))

    def test_listar_e_listar_por_ot(self):
        self._mao_obra(self.ot1.id_ot)
        self._peca(self.ot1.id_ot)
        self._peca(self.ot2.id_ot)
        self.assertEqual(len(self.repo.listar()), 3)
        self.assertEqual(len(self.repo.listar_por_ot(self.ot1.id_ot)), 2)
        self.assertEqual(len(self.repo.listar_por_ot(self.ot2.id_ot)), 1)
        self.assertEqual(self.repo.listar_por_ot(99), [])

    def test_listar_por_peca(self):
        self._peca(self.ot1.id_ot, id_peca=1)
        self._peca(self.ot2.id_ot, id_peca=1)
        self._peca(self.ot2.id_ot, id_peca=2)
        self._mao_obra(self.ot1.id_ot)
        resultado = self.repo.listar_por_peca(1)
        self.assertEqual([self.ot1.id_ot, self.ot2.id_ot],
                         [resultado[0].id_ot, resultado[1].id_ot])
        self.assertEqual(len(resultado), 2)
        self.assertEqual(len(self.repo.listar_por_peca(2)), 1)
        self.assertEqual(self.repo.listar_por_peca(99), [])

    def test_atualizar(self):
        linha = self._peca(self.ot1.id_ot)
        linha.quantidade = 4
        self.assertTrue(self.repo.atualizar(linha))
        self.assertEqual(self.repo.procurar_por_id(linha.id_linha).quantidade, 4)

    def test_apagar(self):
        linha = self._peca(self.ot1.id_ot)
        self.assertTrue(self.repo.apagar(linha.id_linha))
        self.assertFalse(self.repo.apagar(linha.id_linha))

    def test_apagar_por_ot(self):
        self._mao_obra(self.ot1.id_ot)
        self._peca(self.ot1.id_ot)
        self._peca(self.ot2.id_ot)
        self.assertEqual(self.repo.apagar_por_ot(self.ot1.id_ot), 2)
        self.assertEqual(self.repo.listar_por_ot(self.ot1.id_ot), [])
        self.assertEqual(len(self.repo.listar_por_ot(self.ot2.id_ot)), 1)

    def test_regras_da_base_de_dados(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.inserir(LinhaOT(self.ot1.id_ot, "peca", "x", 0, 1))   # quantidade 0
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.inserir(LinhaOT(self.ot1.id_ot, "peca", "x", 1, -5))  # preço negativo
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.inserir(LinhaOT(99, "peca", "x", 1, 1))               # OT inexistente