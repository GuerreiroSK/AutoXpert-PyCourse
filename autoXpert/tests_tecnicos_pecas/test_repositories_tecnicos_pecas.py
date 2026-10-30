import sqlite3
import unittest

from src.repositories import pecas_repository, tecnico_repository
from tests_tecnicos_pecas.base_dados_temporaria import DatabaseTestCase


class TecnicoRepositoryTests(DatabaseTestCase):
    def test_criar_listar_e_obter_tecnico(self):
        id_tecnico = tecnico_repository.criar_tecnico("Ana", "Motor", 20.0)

        self.assertEqual(tecnico_repository.obter_tecnico(id_tecnico)["nome"], "Ana")
        self.assertEqual(len(tecnico_repository.listar_tecnicos(apenas_ativos=True)), 1)

    def test_atualizar_e_eliminar_tecnico(self):
        id_tecnico = tecnico_repository.criar_tecnico("Ana", None, 20.0)

        self.assertTrue(
            tecnico_repository.atualizar_tecnico(id_tecnico, "Ana Silva", None, 22.0, False)
        )
        self.assertEqual(tecnico_repository.listar_tecnicos(apenas_ativos=True), [])
        self.assertTrue(tecnico_repository.eliminar_tecnico(id_tecnico))
        self.assertIsNone(tecnico_repository.obter_tecnico(id_tecnico))


class PecaRepositoryTests(DatabaseTestCase):
    def test_criar_obter_e_listar_peca(self):
        id_peca = pecas_repository.criar_peca("F1", "Filtro", 5.0, 10.0, 2, 2)

        self.assertEqual(pecas_repository.obter_peca(id_peca)["referencia"], "F1")
        self.assertEqual(len(pecas_repository.listar_pecas_com_stock_baixo()), 1)

    def test_atualizar_stock_e_eliminar_peca(self):
        id_peca = pecas_repository.criar_peca("F1", "Filtro", 5.0, 10.0, 2, 1)

        self.assertTrue(pecas_repository.atualizar_stock(id_peca, 2))
        self.assertEqual(pecas_repository.obter_peca(id_peca)["stock_atual"], 4)
        self.assertTrue(pecas_repository.eliminar_peca(id_peca))
        self.assertIsNone(pecas_repository.obter_peca(id_peca))

    def test_referencia_duplicada_e_rejeitada(self):
        pecas_repository.criar_peca("F1", "Filtro", 5.0, 10.0)

        with self.assertRaises(sqlite3.IntegrityError):
            pecas_repository.criar_peca("F1", "Outro filtro", 4.0, 8.0)
