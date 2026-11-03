import sqlite3
import unittest
from unittest.mock import MagicMock, patch

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
            
class TecnicoRepositoryUnitTests(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cursor = self.conn.execute.return_value

        substituicao = patch.object(
            tecnico_repository,
            "get_connection",
            return_value=self.conn,
        )
        self.mock_ligacao = substituicao.start()
        self.addCleanup(substituicao.stop)

    def test_criar_tecnico_devolve_id(self):
        self.cursor.lastrowid = 4

        resultado = tecnico_repository.criar_tecnico(
            "Ana", "Motor", 20.0, True
        )

        self.assertEqual(resultado, 4)
        self.mock_ligacao.assert_called_once_with()
        self.conn.execute.assert_called_once()

        consulta, parametros = self.conn.execute.call_args.args

        self.assertIn("INSERT INTO Tecnico", consulta)
        self.assertEqual(
            parametros,
            ("Ana", "Motor", 20.0, 1),
        )
        self.conn.close.assert_called_once_with()

    def test_obter_tecnico_inexistente_devolve_none(self):
        self.cursor.fetchone.return_value = None

        resultado = tecnico_repository.obter_tecnico(99)

        self.assertIsNone(resultado)
        self.conn.execute.assert_called_once_with(
            "SELECT * FROM Tecnico WHERE id_tecnico = ?",
            (99,),
        )
        self.cursor.fetchone.assert_called_once_with()

    def test_eliminar_tecnico_inexistente_devolve_false(self):
        self.cursor.rowcount = 0

        resultado = tecnico_repository.eliminar_tecnico(99)

        self.assertFalse(resultado)
        self.conn.execute.assert_called_once_with(
            "DELETE FROM Tecnico WHERE id_tecnico = ?",
            (99,),
        )

    def test_obter_propaga_erro_e_fecha_ligacao(self):
        self.conn.execute.side_effect = sqlite3.OperationalError(
            "Falha na consulta"
        )

        with self.assertRaisesRegex(
            sqlite3.OperationalError,
            "Falha na consulta",
        ):
            tecnico_repository.obter_tecnico(4)

        self.conn.close.assert_called_once_with()
class PecaRepositoryUnitTests(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cursor = self.conn.execute.return_value

        substituicao = patch.object(
            pecas_repository,
            "get_connection",
            return_value=self.conn,
        )
        self.mock_ligacao = substituicao.start()
        self.addCleanup(substituicao.stop)

    def test_criar_peca_devolve_id(self):
        self.cursor.lastrowid = 7

        resultado = pecas_repository.criar_peca(
            "F1", "Filtro", 5.0, 10.0, 2, 1, "Loja"
        )

        self.assertEqual(resultado, 7)
        self.conn.execute.assert_called_once()

        consulta, parametros = self.conn.execute.call_args.args

        self.assertIn("INSERT INTO Peca", consulta)
        self.assertEqual(
            parametros,
            ("F1", "Filtro", 2, 1, 5.0, 10.0, "Loja"),
        )

    def test_listar_devolve_linhas_do_cursor(self):
        linhas = [
            {"id_peca": 7, "referencia": "F1"},
            {"id_peca": 8, "referencia": "F2"},
        ]
        self.cursor.fetchall.return_value = linhas

        resultado = pecas_repository.listar_pecas()

        self.assertEqual(resultado, linhas)
        self.conn.execute.assert_called_once_with(
            "SELECT * FROM Peca ORDER BY nome, id_peca"
        )
        self.cursor.fetchall.assert_called_once_with()

    def test_atualizar_stock_envia_variacao(self):
        self.cursor.rowcount = 1

        resultado = pecas_repository.atualizar_stock(7, -2)

        self.assertTrue(resultado)
        self.conn.execute.assert_called_once_with(
            "UPDATE Peca SET stock_atual = stock_atual + ? "
            "WHERE id_peca = ?",
            (-2, 7),
        )

    def test_registar_entrada_stock_envia_dados(self):
        self.cursor.rowcount = 1

        resultado = pecas_repository.registar_entrada_stock(
            7, 3, "Loja", 5.25
        )

        self.assertTrue(resultado)
        self.conn.execute.assert_called_once()

        consulta, parametros = self.conn.execute.call_args.args

        self.assertIn("stock_atual = stock_atual + ?", consulta)
        self.assertEqual(parametros, (3, "Loja", 5.25, 7))

    def test_registar_entrada_rejeita_quantidade_nao_positiva(self):
        for quantidade in [0, -1]:
            with self.subTest(quantidade=quantidade):
                self.mock_ligacao.reset_mock()
                self.conn.reset_mock()

                with self.assertRaises(ValueError):
                    pecas_repository.registar_entrada_stock(
                        7, quantidade, "Loja", 5.25
                    )

                self.mock_ligacao.assert_not_called()
                self.conn.execute.assert_not_called()