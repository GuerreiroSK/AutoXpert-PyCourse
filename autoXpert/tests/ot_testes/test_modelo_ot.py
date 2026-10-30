import unittest

from src.models.ordem_trabalho_model import OrdemTrabalho
from src.models.linha_ot_model import LinhaOT


class TesteOrdemTrabalho(unittest.TestCase):

    def test_estado_por_defeito_e_pendente(self):
        ot = OrdemTrabalho(1, 1, "2026-10-28", "2026-10-30", "Travões a chiar")
        self.assertEqual(ot.estado, "Pendente")
        self.assertIsNone(ot.id_ot)
        self.assertIsNone(ot.data_saida_real)
        self.assertEqual(ot.custo_total, 0)

    def test_lista_de_estados(self):
        self.assertEqual(
            OrdemTrabalho.ESTADOS,
            ["Pendente", "Em Curso", "Aguarda Peça", "Concluída", "Entregue"])

    def test_estado_invalido(self):
        with self.assertRaises(ValueError):
            OrdemTrabalho(1, 1, "2026-10-28", "2026-10-30", "x", estado="Concluida")

    def test_tecnico_obrigatorio(self):
        with self.assertRaises(ValueError):
            OrdemTrabalho(1, None, "2026-10-28", "2026-10-30", "x")


class TesteLinhaOT(unittest.TestCase):

    def test_lista_de_tipos(self):
        self.assertEqual(LinhaOT.TIPOS, ["mao_obra", "peca"])

    def test_tipo_invalido(self):
        with self.assertRaises(ValueError):
            LinhaOT(1, "outro", "x", 1, 1)

    def test_valores_por_defeito(self):
        linha = LinhaOT(1, LinhaOT.TIPO_PECA, "Pastilhas", 2, 25.0, id_peca=1)
        self.assertIsNone(linha.id_linha)
        self.assertIsNone(linha.horas_trabalhadas)

    def test_subtotal(self):
        linha = LinhaOT(1, LinhaOT.TIPO_MAO_OBRA, "Mão-de-obra", 1.5, 40.0)
        self.assertEqual(linha.subtotal(), 60.0)

    def test_subtotal_arredondado_a_duas_casas(self):
        linha = LinhaOT(1, LinhaOT.TIPO_PECA, "Parafuso", 3, 0.1, id_peca=1)
        self.assertEqual(linha.subtotal(), 0.3)