from contextlib import closing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from db import connection


class DatabaseTestCase(unittest.TestCase):
    """Cria uma base temporaria para cada teste."""

    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)

        caminho_bd = Path(pasta.name) / "teste.db"
        substituicao = patch.object(connection, "DB_PATH", caminho_bd)
        substituicao.start()
        self.addCleanup(substituicao.stop)

        connection.inicializar_bd()

    def criar_cliente(self) -> int:
        with closing(connection.get_connection()) as conn:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO Cliente (nome) VALUES (?)",
                    ("Cliente de teste",),
                )
                return cursor.lastrowid

    def criar_ot(self, id_viatura: int, id_tecnico: int) -> int:
        with closing(connection.get_connection()) as conn:
            with conn:
                cursor = conn.execute(
                    """INSERT INTO OrdemTrabalho
                    (id_viatura, id_tecnico, data_entrada, data_prev_saida,
                    estado, descricao_avaria)
                    VALUES (?, ?, '2026-10-28', '2026-10-30', 'Pendente', 'Teste')""",
                    (id_viatura, id_tecnico),
                )
                return cursor.lastrowid
