import unittest

from src.models.tecnico_model import Tecnico


class TestTecnicoModel(unittest.TestCase):

    def test_valores_por_defeito(self):
        tecnico = Tecnico("Ana", None, 20.0)

        self.assertTrue(tecnico.ativo)
        self.assertIsNone(tecnico.id_tecnico)

    def test_guarda_os_dados(self):
        tecnico = Tecnico("Ana", "Motor", 20.5, False, 4)

        self.assertEqual(tecnico.nome, "Ana")
        self.assertEqual(tecnico.especialidade, "Motor")
        self.assertEqual(tecnico.custo_hora, 20.5)
        self.assertFalse(tecnico.ativo)
        self.assertEqual(tecnico.id_tecnico, 4)
