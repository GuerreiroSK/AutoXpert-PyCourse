import unittest

from src.models.log_alteracao_ot_model import LogAlteracaoOT
from src.repositories.log_alteracao_ot_repository import LogAlteracaoOTRepository
from tests.bd_testes.base_dados_teste import criar_conexao_teste


class TestLogAlteracaoOTRepository(unittest.TestCase):
    # Testes de integração: repositório + base de dados SQLite em memória.

    def setUp(self):
        self.conexao = criar_conexao_teste()
        for descricao in ("Avaria 1", "Avaria 2"):
            self.conexao.execute(
                "INSERT INTO OrdemTrabalho (id_viatura, id_tecnico, data_entrada, "
                "data_prev_saida, estado, descricao_avaria) "
                "VALUES (1, 1, '2026-11-03', '2026-11-05', 'Pendente', ?)", (descricao,))
        self.conexao.commit()
        self.repo = LogAlteracaoOTRepository(self.conexao)

    def tearDown(self):
        self.conexao.close()

    def test_inserir_preenche_o_id(self):
        log = LogAlteracaoOT(1, "2026-11-03 10:00:00", "estado", None, "Pendente", "Em curso")

        guardado = self.repo.inserir(log)

        self.assertIs(guardado, log)
        self.assertEqual(log.id_log, 1)

    def test_inserir_sem_data_usa_a_data_atual(self):
        log = LogAlteracaoOT(1, None, "estado", None, "Pendente", "Em curso")

        self.repo.inserir(log)

        self.assertTrue(len(log.data_hora) > 0)

    def test_obter_por_id_devolve_os_dados_certos(self):
        self.repo.inserir(LogAlteracaoOT(1, "2026-11-03 10:00:00", "estado", None,
                                          "Pendente", "Em curso"))

        log = self.repo.obter_por_id(1)

        self.assertIsInstance(log, LogAlteracaoOT)
        self.assertEqual(log.id_ot, 1)
        self.assertEqual(log.campo_alterado, "estado")
        self.assertEqual(log.valor_anterior, "Pendente")
        self.assertEqual(log.valor_novo, "Em curso")

    def test_obter_inexistente_devolve_none(self):
        self.assertIsNone(self.repo.obter_por_id(99))

    def test_listar_por_ot_mais_recentes_primeiro(self):
        self.repo.inserir(LogAlteracaoOT(1, "2026-11-03 10:00:00", "estado"))
        self.repo.inserir(LogAlteracaoOT(1, "2026-11-03 12:00:00", "tecnico"))
        self.repo.inserir(LogAlteracaoOT(2, "2026-11-03 11:00:00", "estado"))

        campos = []
        for log in self.repo.listar_por_ot(1):
            campos.append(log.campo_alterado)

        self.assertEqual(campos, ["tecnico", "estado"])
        self.assertEqual(len(self.repo.listar_todos()), 3)

    def test_eliminar(self):
        self.repo.inserir(LogAlteracaoOT(1, "2026-11-03 10:00:00", "estado"))

        self.assertTrue(self.repo.eliminar(1))
        self.assertFalse(self.repo.eliminar(1))
