import sqlite3
import unittest

from src.models.viatura_model import Viatura
from src.repositories.viatura_repository import ViaturaRepository
from tests.bd_testes.base_dados_teste import criar_conexao_vazia


class TestViaturaRepository(unittest.TestCase):
    # Testes de integração: repositório + base de dados SQLite em memória.

    def setUp(self):
        self.conexao = criar_conexao_vazia()
        self.conexao.execute("INSERT INTO Cliente (nome) VALUES ('Ana')")
        self.conexao.execute("INSERT INTO Cliente (nome) VALUES ('Rui')")
        self.conexao.commit()
        self.repo = ViaturaRepository(self.conexao)

    def tearDown(self):
        self.conexao.close()

    def nova(self, matricula="AA-11-BB", id_cliente=1):
        viatura = Viatura(matricula, "Renault", "Clio", id_cliente, ano=2018, cor="Azul",
                          km_estrada=1000)
        self.repo.criar(viatura)
        return viatura

    def test_criar_preenche_o_id(self):
        viatura = self.nova()

        self.assertEqual(viatura.id_viatura, 1)

    def test_obter_por_id_devolve_os_dados_certos(self):
        self.nova()

        viatura = self.repo.obter_por_id(1)

        self.assertIsInstance(viatura, Viatura)
        self.assertEqual(viatura.matricula, "AA-11-BB")
        self.assertEqual(viatura.marca, "Renault")
        self.assertEqual(viatura.modelo, "Clio")
        self.assertEqual(viatura.ano, 2018)
        self.assertEqual(viatura.cor, "Azul")
        self.assertEqual(viatura.km_estrada, 1000)
        self.assertEqual(viatura.id_cliente, 1)

    def test_obter_inexistente_devolve_none(self):
        self.assertIsNone(self.repo.obter_por_id(99))
        self.assertIsNone(self.repo.obter_por_matricula("XX-00-XX"))

    def test_obter_por_matricula(self):
        self.nova("CC-22-DD")

        self.assertEqual(self.repo.obter_por_matricula("CC-22-DD").id_viatura, 1)

    def test_matricula_repetida_e_recusada(self):
        self.nova("AA-11-BB")

        with self.assertRaises(sqlite3.IntegrityError):
            self.nova("AA-11-BB")

    def test_cliente_inexistente_e_recusado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.nova("AA-11-BB", id_cliente=99)

    def test_listar_todas_e_por_cliente(self):
        self.nova("AA-11-BB", 1)
        self.nova("CC-22-DD", 1)
        self.nova("EE-33-FF", 2)

        self.assertEqual(len(self.repo.listar_todas()), 3)
        self.assertEqual(len(self.repo.listar_por_cliente(1)), 2)
        self.assertEqual(len(self.repo.listar_por_cliente(2)), 1)
        self.assertEqual(self.repo.listar_por_cliente(99), [])

    def test_atualizar(self):
        viatura = self.nova()
        viatura.cor = "Preto"
        viatura.km_estrada = 2000

        self.assertTrue(self.repo.atualizar(viatura))

        guardada = self.repo.obter_por_id(1)
        self.assertEqual(guardada.cor, "Preto")
        self.assertEqual(guardada.km_estrada, 2000)

    def test_atualizar_sem_id_ou_inexistente_devolve_false(self):
        self.assertFalse(self.repo.atualizar(Viatura("XX-00-XX", "A", "B", 1)))
        self.assertFalse(self.repo.atualizar(Viatura("XX-00-XX", "A", "B", 1, 99)))

    def test_eliminar(self):
        self.nova()

        self.assertTrue(self.repo.eliminar(1))
        self.assertIsNone(self.repo.obter_por_id(1))
        self.assertFalse(self.repo.eliminar(1))
