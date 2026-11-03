import sqlite3
import unittest

from src.models.tecnico_model import Tecnico
from src.repositories.tecnico_repository import TecnicoRepository
from tests.bd_testes.base_dados_teste import criar_conexao_vazia


class TestTecnicoRepository(unittest.TestCase):
    # Testes de integração: repositório + base de dados SQLite em memória
    # (com o schema real e tabelas vazias).

    def setUp(self):
        self.conexao = criar_conexao_vazia()
        self.repo = TecnicoRepository(self.conexao)

    def tearDown(self):
        self.conexao.close()

    def test_inserir_preenche_o_id(self):
        tecnico = self.repo.inserir(Tecnico("Ana", "Motor", 20.0))

        self.assertEqual(tecnico.id_tecnico, 1)

    def test_obter_por_id_devolve_um_tecnico_com_os_dados_certos(self):
        self.repo.inserir(Tecnico("Ana", "Motor", 20.0))

        tecnico = self.repo.obter_por_id(1)

        self.assertIsInstance(tecnico, Tecnico)
        self.assertEqual(tecnico.nome, "Ana")
        self.assertEqual(tecnico.especialidade, "Motor")
        self.assertEqual(tecnico.custo_hora, 20.0)
        self.assertIs(tecnico.ativo, True)    # a base de dados guarda 1; o objeto tem True

    def test_obter_por_id_inexistente_devolve_none(self):
        self.assertIsNone(self.repo.obter_por_id(99))

    def test_listar_por_ordem_alfabetica(self):
        self.repo.inserir(Tecnico("Rui", None, 30.0))
        self.repo.inserir(Tecnico("Ana", None, 20.0))

        nomes = []
        for tecnico in self.repo.listar_todos():
            nomes.append(tecnico.nome)

        self.assertEqual(nomes, ["Ana", "Rui"])

    def test_listar_apenas_ativos(self):
        self.repo.inserir(Tecnico("Ana", None, 20.0, True))
        self.repo.inserir(Tecnico("Rui", None, 30.0, False))

        ativos = self.repo.listar_todos(apenas_ativos=True)

        self.assertEqual(len(ativos), 1)
        self.assertEqual(ativos[0].nome, "Ana")
        self.assertEqual(len(self.repo.listar_todos()), 2)

    def test_atualizar(self):
        tecnico = self.repo.inserir(Tecnico("Ana", None, 20.0))
        tecnico.nome = "Ana Silva"
        tecnico.custo_hora = 22.0
        tecnico.ativo = False

        self.assertTrue(self.repo.atualizar(tecnico))

        guardado = self.repo.obter_por_id(1)
        self.assertEqual(guardado.nome, "Ana Silva")
        self.assertEqual(guardado.custo_hora, 22.0)
        self.assertIs(guardado.ativo, False)

    def test_atualizar_inexistente_devolve_false(self):
        self.assertFalse(self.repo.atualizar(Tecnico("Ana", None, 20.0, True, 99)))

    def test_eliminar(self):
        self.repo.inserir(Tecnico("Ana", None, 20.0))

        self.assertTrue(self.repo.eliminar(1))
        self.assertIsNone(self.repo.obter_por_id(1))

    def test_eliminar_inexistente_devolve_false(self):
        self.assertFalse(self.repo.eliminar(99))

    def test_custo_hora_negativo_e_recusado_pela_base_de_dados(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.inserir(Tecnico("Ana", None, -1.0))

    def test_tecnico_com_ots_nao_pode_ser_eliminado(self):
        self.repo.inserir(Tecnico("Ana", None, 20.0))
        self.conexao.execute("INSERT INTO Cliente (nome) VALUES ('C')")
        self.conexao.execute("INSERT INTO Viatura (matricula, marca, modelo, id_cliente) "
                             "VALUES ('AA-11-BB', 'R', 'C', 1)")
        self.conexao.execute(
            "INSERT INTO OrdemTrabalho (id_viatura, id_tecnico, data_entrada, "
            "data_prev_saida, estado, descricao_avaria) "
            "VALUES (1, 1, '2026-11-03', '2026-11-05', 'Pendente', 'Teste')")
        self.conexao.commit()

        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.eliminar(1)
