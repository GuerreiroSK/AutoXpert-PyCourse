import unittest
from unittest.mock import MagicMock

from src.models.log_alteracao_ot_model import LogAlteracaoOT
from src.services.log_alteracao_ot_service import LogAlteracaoOTService


class TestLogAlteracaoOTService(unittest.TestCase):

    def setUp(self):
        # Mocks limpos antes de cada teste: nem a base de dados nem os repositórios são reais
        self.mock_repo = MagicMock()
        self.mock_ot_repo = MagicMock()
        # Por defeito, a OT existe
        self.mock_ot_repo.procurar_por_id.return_value = MagicMock()

        self.svc = LogAlteracaoOTService(self.mock_repo, self.mock_ot_repo)

    # ----- registar_alteracao: validações -----

    def test_id_ot_invalido_levanta_erro(self):
        for id_ot in (0, -1):
            with self.subTest(id_ot=id_ot):
                with self.assertRaises(ValueError):
                    self.svc.registar_alteracao(id_ot, "estado", "Pendente", "Concluída")
                self.mock_repo.registar.assert_not_called()

    def test_campo_vazio_ou_so_espacos_levanta_erro(self):
        casos = [("", "vazio"), ("   ", "só espaços"), (None, "None")]
        for campo, descricao in casos:
            with self.subTest(caso=descricao):
                with self.assertRaises(ValueError):
                    self.svc.registar_alteracao(1, campo, "Pendente", "Concluída")
                self.mock_repo.registar.assert_not_called()

    def test_ot_inexistente_levanta_erro(self):
        self.mock_ot_repo.procurar_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.registar_alteracao(99, "estado", "Pendente", "Concluída")

        self.mock_repo.registar.assert_not_called()

    # ----- registar_alteracao: caminho feliz -----

    def test_registar_chama_o_repositorio_uma_vez(self):
        self.svc.registar_alteracao(1, "estado", "Pendente", "Em Curso")

        self.mock_repo.registar.assert_called_once()

    def test_registar_passa_um_objeto_com_os_dados_certos(self):
        self.svc.registar_alteracao(1, "  estado  ", "Pendente", "Em Curso")

        registo = self.mock_repo.registar.call_args[0][0]
        self.assertIsInstance(registo, LogAlteracaoOT)   # e não um dicionário
        self.assertEqual(registo.id_ot, 1)
        self.assertEqual(registo.campo_alterado, "estado")   # sem espaços
        self.assertEqual(registo.valor_anterior, "Pendente")
        self.assertEqual(registo.valor_novo, "Em Curso")
        self.assertTrue(registo.data_hora)   # preenchida pelo service
        self.assertIsNone(registo.id_log)    # ainda sem ID do repositório

    def test_registar_devolve_o_registo_criado(self):
        resultado = self.svc.registar_alteracao(1, "estado", "Pendente", "Em Curso")

        self.assertIsInstance(resultado, LogAlteracaoOT)
        self.assertEqual(resultado.campo_alterado, "estado")

    def test_erro_do_repositorio_propaga(self):
        self.mock_repo.registar.side_effect = RuntimeError("BD off")

        with self.assertRaises(RuntimeError):
            self.svc.registar_alteracao(1, "estado", "Pendente", "Em Curso")

    # ----- consultar_alteracao -----

    def test_consultar_devolve_o_registo_do_repositorio(self):
        esperado = LogAlteracaoOT(1, "2026-11-03 10:00:00", "estado", id_log=5)
        self.mock_repo.obter_por_id.return_value = esperado

        resultado = self.svc.consultar_alteracao(5)

        self.assertEqual(resultado.id_log, 5)
        self.mock_repo.obter_por_id.assert_called_once_with(5)

    def test_consultar_inexistente_levanta_erro(self):
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.consultar_alteracao(99)

    def test_consultar_id_invalido_nao_chama_o_repositorio(self):
        for id_log in (0, -3):
            with self.subTest(id_log=id_log):
                with self.assertRaises(ValueError):
                    self.svc.consultar_alteracao(id_log)
                self.mock_repo.obter_por_id.assert_not_called()

    # ----- listar -----

    def test_listar_por_ot_devolve_a_lista_do_repositorio(self):
        lista = [
            LogAlteracaoOT(1, "2026-11-03 10:00:00", "estado", id_log=1),
            LogAlteracaoOT(1, "2026-11-03 11:00:00", "técnico", id_log=2),
        ]
        self.mock_repo.listar_por_ot.return_value = lista

        resultado = self.svc.listar_alteracoes_por_ot(1)

        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0].campo_alterado, "estado")
        self.mock_repo.listar_por_ot.assert_called_once_with(1)

    def test_listar_por_ot_inexistente_levanta_erro(self):
        self.mock_ot_repo.procurar_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.listar_alteracoes_por_ot(99)

        self.mock_repo.listar_por_ot.assert_not_called()

    def test_listar_por_ot_com_id_invalido(self):
        with self.assertRaises(ValueError):
            self.svc.listar_alteracoes_por_ot(0)

        self.mock_repo.listar_por_ot.assert_not_called()

    def test_listar_todas_devolve_a_lista_do_repositorio(self):
        self.mock_repo.listar_todos.return_value = [MagicMock(), MagicMock(), MagicMock()]

        resultado = self.svc.listar_todas_alteracoes()

        self.assertEqual(len(resultado), 3)
        self.mock_repo.listar_todos.assert_called_once()

    def test_listar_todas_vazio(self):
        self.mock_repo.listar_todos.return_value = []

        self.assertEqual(self.svc.listar_todas_alteracoes(), [])
