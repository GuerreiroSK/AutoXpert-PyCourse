import sqlite3
import unittest

from src.models.cliente_model import Cliente
from src.repositories.cliente_repository import ClienteRepository
from tests.bd_testes.base_dados_teste import criar_conexao_vazia


class TestClienteRepository(unittest.TestCase):
    # Testes de integração: repositório + base de dados SQLite em memória.

    def setUp(self):
        self.conexao = criar_conexao_vazia()
        self.repo = ClienteRepository(self.conexao)

    def tearDown(self):
        self.conexao.close()

    # A data de registo é preenchida pelo service; aqui damos uma data fixa
    def novo(self, nome, nif=None, telefone=None, email=None, morada=None):
        return Cliente(nome, nif, telefone, email, morada, "2026-11-03")

    def test_inserir_preenche_o_id(self):
        cliente = self.repo.inserir(self.novo("Ana", "123456789"))

        self.assertEqual(cliente.id_cliente, 1)

    def test_obter_por_id_devolve_os_dados_certos(self):
        self.repo.inserir(self.novo("Ana", "123456789", "912345678", "a@a.pt", "Rua 1"))

        cliente = self.repo.obter_por_id(1)

        self.assertIsInstance(cliente, Cliente)
        self.assertEqual(cliente.nome, "Ana")
        self.assertEqual(cliente.nif, "123456789")
        self.assertEqual(cliente.telefone, "912345678")
        self.assertEqual(cliente.email, "a@a.pt")
        self.assertEqual(cliente.morada, "Rua 1")
        self.assertEqual(cliente.data_registo, "2026-11-03")

    def test_obter_inexistente_devolve_none(self):
        self.assertIsNone(self.repo.obter_por_id(99))

    def test_nif_repetido_e_recusado(self):
        self.repo.inserir(self.novo("Ana", "123456789"))

        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.inserir(self.novo("Rui", "123456789"))

    def test_listar_todos(self):
        self.repo.inserir(self.novo("Ana", "111111111"))
        self.repo.inserir(self.novo("Rui", "222222222"))

        self.assertEqual(len(self.repo.listar_todos()), 2)

    def test_atualizar(self):
        cliente = self.repo.inserir(self.novo("Ana", "111111111"))
        cliente.nome = "Ana Silva"
        cliente.telefone = "912345678"

        self.assertTrue(self.repo.atualizar(cliente))

        guardado = self.repo.obter_por_id(1)
        self.assertEqual(guardado.nome, "Ana Silva")
        self.assertEqual(guardado.telefone, "912345678")

    def test_atualizar_inexistente_devolve_false(self):
        self.assertFalse(self.repo.atualizar(Cliente("Ana", None, None, None, None, None, 99)))

    def test_eliminar(self):
        self.repo.inserir(self.novo("Ana", "111111111"))

        self.assertTrue(self.repo.eliminar(1))
        self.assertIsNone(self.repo.obter_por_id(1))
        self.assertFalse(self.repo.eliminar(1))

    def test_cliente_com_viaturas_nao_pode_ser_eliminado(self):
        self.repo.inserir(self.novo("Ana", "111111111"))
        self.conexao.execute("INSERT INTO Viatura (matricula, marca, modelo, id_cliente) "
                             "VALUES ('AA-11-BB', 'Renault', 'Clio', 1)")
        self.conexao.commit()

        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.eliminar(1)
