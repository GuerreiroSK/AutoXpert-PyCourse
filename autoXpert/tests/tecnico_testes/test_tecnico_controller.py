import unittest
from unittest.mock import MagicMock

from src.controllers.tecnico_controller import TecnicoController
from src.models.tecnico_model import Tecnico


class TestTecnicoController(unittest.TestCase):

    def setUp(self):
        self.servico = MagicMock()
        self.controller = TecnicoController(self.servico)

    def test_listar_obter_e_eliminar_chamam_o_servico(self):
        self.controller.listar(True)
        self.controller.obter(8)
        self.controller.eliminar(8)

        self.servico.listar.assert_called_once_with(True)
        self.servico.obter.assert_called_once_with(8)
        self.servico.eliminar.assert_called_once_with(8)

    def test_guardar_converte_os_dados_e_chama_o_servico(self):
        dados = {"nome": "Ana", "especialidade": "Motor", "custo_hora": "20,50"}

        self.controller.guardar(dados, False, 8)

        enviado = self.servico.guardar.call_args[0][0]
        self.assertEqual(enviado.nome, "Ana")
        self.assertEqual(enviado.especialidade, "Motor")
        self.assertEqual(enviado.custo_hora, 20.5)   # a vírgula passa a ponto
        self.assertFalse(enviado.ativo)
        self.assertEqual(enviado.id_tecnico, 8)

    def test_guardar_devolve_o_que_o_servico_devolve(self):
        esperado = Tecnico("Ana", "Motor", 20.0, True, 8)
        self.servico.guardar.return_value = esperado
        dados = {"nome": "Ana", "especialidade": "Motor", "custo_hora": "20"}

        self.assertIs(self.controller.guardar(dados, True), esperado)

    def test_guardar_rejeita_custo_hora_invalido(self):
        for custo in ("", "vinte", "20,5,0"):
            with self.subTest(custo=custo):
                dados = {"nome": "Ana", "especialidade": "Motor", "custo_hora": custo}

                with self.assertRaises(ValueError):
                    self.controller.guardar(dados, True)

                self.servico.guardar.assert_not_called()

    def test_obter_propaga_o_erro_do_servico(self):
        self.servico.obter.side_effect = ValueError("O técnico selecionado já não existe.")

        with self.assertRaisesRegex(ValueError, "já não existe"):
            self.controller.obter(99)
