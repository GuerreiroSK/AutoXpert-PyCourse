import unittest

from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.repositories.linha_ot_repository import LinhaOTRepository
from src.services.ot_service import OrdemTrabalhoService
from src.services.linha_ot_service import LinhaOTService
from src.controllers.ot_controller import OrdemTrabalhoController
from src.controllers.linha_ot_controller import LinhaOTController
from tests.bd_testes.base_dados_teste import criar_conexao_teste


class TesteLinhaOTController(unittest.TestCase):
    # O controller recebe texto (como vem da janela) e devolve sempre (ok, resultado).

    def setUp(self):
        self.conexao = criar_conexao_teste()
        ot_service = OrdemTrabalhoService(OrdemTrabalhoRepository(self.conexao))
        linha_service = LinhaOTService(LinhaOTRepository(self.conexao), ot_service)
        self.ot_controller = OrdemTrabalhoController(ot_service)
        self.controller = LinhaOTController(linha_service)

    def tearDown(self):
        self.conexao.close()

    # Cria a OT 1 (precisa de existir para lhe juntar linhas)
    def _criar_ot(self):
        return self.ot_controller.criar_ot("1", "1", "2026-10-28", "2026-10-30",
                                           "Travões a chiar")

    def test_lista_de_tipos_de_linha(self):
        self.assertEqual(self.controller.lista_tipos_linha(), ["mao_obra", "peca"])

    def test_adicionar_linhas_aceita_virgula_e_recalcula_o_custo(self):
        self._criar_ot()
        ok, linha = self.controller.adicionar_linha(
            1, "mao_obra", "Substituir pastilhas", "1,5", "40", "1,5", "")
        self.assertTrue(ok)
        self.assertEqual(linha.quantidade, 1.5)
        self.assertEqual(linha.horas_trabalhadas, 1.5)
        self.assertIsNone(linha.id_peca)
        ok, linha = self.controller.adicionar_linha(1, "peca", "Pastilhas", "2", "25,50", "", "1")
        self.assertTrue(ok)
        self.assertEqual(linha.id_peca, 1)
        self.assertEqual(self.ot_controller.obter_ot(1)[1].custo_total, 111.0)
        ok, linhas = self.controller.listar_linhas(1)
        self.assertEqual(len(linhas), 2)

    def test_adicionar_linha_com_numeros_invalidos(self):
        self._criar_ot()
        self.assertEqual(self.controller.adicionar_linha(1, "mao_obra", "x", "abc", "10"),
                         (False, "A quantidade tem de ser um número"))
        self.assertEqual(self.controller.adicionar_linha(1, "mao_obra", "x", "1", "dez"),
                         (False, "O preço unitário tem de ser um número"))
        self.assertEqual(self.controller.adicionar_linha(1, "mao_obra", "x", "1", "10", "muitas"),
                         (False, "As horas trabalhadas tem de ser um número"))
        self.assertEqual(self.controller.adicionar_linha(1, "peca", "x", "1", "10", "", "a"),
                         (False, "A peça tem de ser um número inteiro"))

    def test_adicionar_linha_com_campos_em_falta(self):
        self._criar_ot()
        self.assertEqual(self.controller.adicionar_linha(1, "mao_obra", "x", "", "10"),
                         (False, "A quantidade tem de ser maior que zero"))
        self.assertEqual(self.controller.adicionar_linha(1, "mao_obra", "x", "1", ""),
                         (False, "O preço unitário não pode ser negativo"))
        self.assertEqual(self.controller.adicionar_linha(1, "peca", "x", "1", "10"),
                         (False, "Uma linha de peça tem de indicar a peça usada"))
        self.assertEqual(self.controller.adicionar_linha(1, "mao_obra", " ", "1", "10"),
                         (False, "A descrição da linha é obrigatória"))
        self.assertEqual(self.controller.listar_linhas(1), (True, []))

    def test_adicionar_linha_a_peca_inexistente(self):
        self._criar_ot()
        self.assertEqual(self.controller.adicionar_linha(1, "peca", "x", "1", "10", "", "99"),
                         (False, "A peça indicada não existe"))

    def test_remover_linha(self):
        self._criar_ot()
        ok, linha = self.controller.adicionar_linha(1, "mao_obra", "Trabalho", "1", "40")
        self.assertEqual(self.controller.remover_linha(linha.id_linha), (True, None))
        self.assertEqual(self.ot_controller.obter_ot(1)[1].custo_total, 0)
        self.assertEqual(self.controller.remover_linha(linha.id_linha),
                         (False, "Linha não encontrada: " + str(linha.id_linha)))

    def test_ot_entregue_nao_aceita_linhas(self):
        self._criar_ot()
        self.ot_controller.mudar_estado(1, "Concluída")
        self.ot_controller.mudar_estado(1, "Entregue", "2026-10-31")
        ok, mensagem = self.controller.adicionar_linha(1, "mao_obra", "x", "1", "10")
        self.assertFalse(ok)
        self.assertIn("não pode ser alterada", mensagem)

    def test_listar_linhas_de_ot_inexistente(self):
        ok, mensagem = self.controller.listar_linhas(99)
        self.assertFalse(ok)
        self.assertIn("99", mensagem)

    def test_remover_linha_inexistente(self):
        self.assertEqual(self.controller.remover_linha(99),
                         (False, "Linha não encontrada: 99"))

    def test_erro_inesperado_da_base_de_dados_vira_mensagem(self):
        self._criar_ot()
        self.conexao.close()  # simula uma base de dados indisponível
        ok, mensagem = self.controller.listar_linhas(1)
        self.assertFalse(ok)
        self.assertTrue(mensagem.startswith("Erro na base de dados: "))
