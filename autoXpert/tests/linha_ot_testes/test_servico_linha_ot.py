import unittest

from src.models.ordem_trabalho_model import OrdemTrabalho
from src.models.linha_ot_model import LinhaOT
from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.repositories.linha_ot_repository import LinhaOTRepository
from src.services.ot_service import OrdemTrabalhoService
from src.services.linha_ot_service import LinhaOTService
from tests.bd_testes.base_dados_teste import criar_conexao_teste


class TesteLinhaOTService(unittest.TestCase):

    def setUp(self):
        self.conexao = criar_conexao_teste()
        self.repo_ot = OrdemTrabalhoRepository(self.conexao)
        self.repo_linha = LinhaOTRepository(self.conexao)
        self.ot_service = OrdemTrabalhoService(self.repo_ot)
        self.service = LinhaOTService(self.repo_linha, self.ot_service)

    def tearDown(self):
        self.conexao.close()

    def _criar_ot(self, id_viatura=1):
        return self.ot_service.criar_ot(id_viatura, 1, "2026-10-28", "2026-10-30",
                                        "Travões a chiar")

    # OT com uma linha que passou por Concluída e Entregue (já não pode ser alterada)
    def _criar_ot_entregue(self):
        ot = self._criar_ot()
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "Trabalho", 1, 50)
        self.ot_service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_CONCLUIDA)
        self.ot_service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_ENTREGUE,
                                     data_saida_real="2026-10-30")
        return ot

    def test_adicionar_linhas_recalcula_o_custo(self):
        ot = self._criar_ot()
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA,
                                     "Substituir pastilhas", 1.5, 40.0,
                                     horas_trabalhadas=1.5)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 60.0)
        linha = self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA,
                                             "Pastilhas", 2, 25.0, id_peca=1)
        self.assertEqual(linha.id_linha, 2)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 110.0)

    def test_remover_linha_recalcula_o_custo(self):
        ot = self._criar_ot()
        l1 = self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "Trabalho", 1, 40)
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA, "Filtro", 1, 15.5, id_peca=1)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 55.5)
        self.service.remover_linha(l1.id_linha)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 15.5)
        self.assertEqual(len(self.service.listar_linhas(ot.id_ot)), 1)

    def test_remover_ultima_linha_poe_custo_a_zero(self):
        ot = self._criar_ot()
        linha = self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "Trabalho", 1, 40)
        self.service.remover_linha(linha.id_linha)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 0)

    def test_custo_e_arredondado_a_duas_casas(self):
        ot = self._criar_ot()
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA, "Parafuso", 3, 0.1, id_peca=1)
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA, "Porca", 3, 0.2, id_peca=2)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 0.9)

    def test_adicionar_linha_valida_os_dados(self):
        ot = self._criar_ot()
        with self.assertRaises(ValueError):   # descrição vazia
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, " ", 1, 10)
        with self.assertRaises(ValueError):   # quantidade 0
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "x", 0, 10)
        with self.assertRaises(ValueError):   # preço negativo
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "x", 1, -1)
        with self.assertRaises(ValueError):   # tipo inválido
            self.service.adicionar_linha(ot.id_ot, "outro", "x", 1, 10)
        with self.assertRaises(ValueError):   # peça sem indicar a peça
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA, "x", 1, 10)
        with self.assertRaises(ValueError):   # mão-de-obra com peça
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "x", 1, 10, id_peca=1)
        self.assertEqual(self.service.listar_linhas(ot.id_ot), [])
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 0)

    def test_adicionar_linha_a_ot_inexistente(self):
        with self.assertRaises(ValueError):
            self.service.adicionar_linha(99, LinhaOT.TIPO_MAO_OBRA, "x", 1, 10)

    def test_ot_entregue_nao_aceita_nem_perde_linhas(self):
        ot = self._criar_ot_entregue()
        linhas = self.service.listar_linhas(ot.id_ot)
        with self.assertRaises(ValueError):
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "x", 1, 10)
        with self.assertRaises(ValueError):
            self.service.remover_linha(linhas[0].id_linha)
        self.assertEqual(len(self.service.listar_linhas(ot.id_ot)), 1)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 50)

    def test_remover_linha_inexistente(self):
        with self.assertRaises(ValueError):
            self.service.remover_linha(99)

    def test_listar_linhas_de_ot_inexistente(self):
        with self.assertRaises(ValueError):
            self.service.listar_linhas(99)

    def test_recalcular_custo_devolve_o_total_e_guarda_na_ot(self):
        ot = self._criar_ot()
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "Trabalho", 2, 30)
        self.ot_service.atualizar_custo_total(ot.id_ot, 999)   # custo desatualizado
        self.assertEqual(self.service.recalcular_custo(ot.id_ot), 60)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 60)

    def test_cada_ot_so_ve_e_conta_as_suas_linhas(self):
        ot1 = self._criar_ot(id_viatura=1)
        ot2 = self._criar_ot(id_viatura=2)
        self.service.adicionar_linha(ot1.id_ot, LinhaOT.TIPO_MAO_OBRA, "A", 1, 10)
        linha2 = self.service.adicionar_linha(ot2.id_ot, LinhaOT.TIPO_MAO_OBRA, "B", 1, 20)
        self.assertEqual(len(self.service.listar_linhas(ot1.id_ot)), 1)
        self.service.remover_linha(linha2.id_linha)
        self.assertEqual(self.repo_ot.procurar_por_id(ot1.id_ot).custo_total, 10)
        self.assertEqual(self.repo_ot.procurar_por_id(ot2.id_ot).custo_total, 0)
