import unittest

from src.models.ordem_trabalho_model import OrdemTrabalho


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
