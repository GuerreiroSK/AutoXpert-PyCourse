import unittest
from unittest.mock import MagicMock

from src.models.tecnico_model import Tecnico
from src.services.tecnico_service import TecnicoService


class TestTecnicoService(unittest.TestCase):
    # Testes unitários: o repositório é MagicMock, por isso não há base de dados.

    def setUp(self):
        self.mock_repo = MagicMock()
        self.svc = TecnicoService(self.mock_repo)

    # ----- guardar (criar) -----

    def test_guardar_novo_limpa_o_texto_e_insere(self):
        self.mock_repo.inserir.side_effect = self._dar_id_4

        tecnico = self.svc.guardar(Tecnico(" Ana ", " Motor ", 20.0))

        self.mock_repo.inserir.assert_called_once()
        enviado = self.mock_repo.inserir.call_args[0][0]
        self.assertEqual(enviado.nome, "Ana")
        self.assertEqual(enviado.especialidade, "Motor")
        self.assertEqual(tecnico.id_tecnico, 4)
        self.mock_repo.atualizar.assert_not_called()

    # O repositório verdadeiro preenche o id; o mock faz o mesmo
    def _dar_id_4(self, tecnico):
        tecnico.id_tecnico = 4
        return tecnico

    def test_guardar_especialidade_vazia_fica_none(self):
        for especialidade in ("", "   ", None):
            with self.subTest(especialidade=especialidade):
                self.svc.guardar(Tecnico("Ana", especialidade, 20.0))

                enviado = self.mock_repo.inserir.call_args[0][0]
                self.assertIsNone(enviado.especialidade)

    def test_guardar_rejeita_nome_vazio(self):
        for nome in ("", "   "):
            with self.subTest(nome=nome):
                with self.assertRaises(ValueError):
                    self.svc.guardar(Tecnico(nome, None, 20.0))
                self.mock_repo.inserir.assert_not_called()

    def test_guardar_rejeita_custo_hora_invalido(self):
        for custo in (-1.0, float("nan"), float("inf")):
            with self.subTest(custo=custo):
                with self.assertRaises(ValueError):
                    self.svc.guardar(Tecnico("Ana", None, custo))
                self.mock_repo.inserir.assert_not_called()

    def test_guardar_aceita_custo_hora_zero(self):
        self.svc.guardar(Tecnico("Ana", None, 0.0))

        self.mock_repo.inserir.assert_called_once()

    def test_guardar_rejeita_ativo_que_nao_seja_booleano(self):
        with self.assertRaises(ValueError):
            self.svc.guardar(Tecnico("Ana", None, 20.0, "sim"))

        self.mock_repo.inserir.assert_not_called()

    # ----- guardar (atualizar) -----

    def test_guardar_existente_atualiza(self):
        self.mock_repo.atualizar.return_value = True

        tecnico = self.svc.guardar(Tecnico(" Ana Silva ", " Motor ", 22.0, False, 4))

        self.mock_repo.atualizar.assert_called_once()
        enviado = self.mock_repo.atualizar.call_args[0][0]
        self.assertEqual(enviado.id_tecnico, 4)
        self.assertEqual(enviado.nome, "Ana Silva")
        self.assertFalse(enviado.ativo)
        self.assertEqual(tecnico.nome, "Ana Silva")
        self.mock_repo.inserir.assert_not_called()

    def test_guardar_existente_inexistente_levanta_erro(self):
        self.mock_repo.atualizar.return_value = False

        with self.assertRaises(ValueError):
            self.svc.guardar(Tecnico("Ana", None, 20.0, True, 99))

    # ----- listar / obter / eliminar -----

    def test_listar_devolve_a_lista_do_repositorio(self):
        lista = [Tecnico("Ana", None, 20.0, True, 1)]
        self.mock_repo.listar_todos.return_value = lista

        resultado = self.svc.listar()

        self.assertEqual(resultado, lista)
        self.mock_repo.listar_todos.assert_called_once_with(False)

    def test_listar_apenas_ativos_passa_o_filtro(self):
        self.svc.listar(True)

        self.mock_repo.listar_todos.assert_called_once_with(True)

    def test_obter_devolve_o_tecnico(self):
        esperado = Tecnico("Ana", None, 20.0, True, 4)
        self.mock_repo.obter_por_id.return_value = esperado

        self.assertIs(self.svc.obter(4), esperado)
        self.mock_repo.obter_por_id.assert_called_once_with(4)

    def test_obter_inexistente_levanta_erro(self):
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.obter(99)

    def test_eliminar_chama_o_repositorio(self):
        self.mock_repo.eliminar.return_value = True

        self.svc.eliminar(4)

        self.mock_repo.eliminar.assert_called_once_with(4)

    def test_eliminar_inexistente_levanta_erro(self):
        self.mock_repo.eliminar.return_value = False

        with self.assertRaises(ValueError):
            self.svc.eliminar(99)
