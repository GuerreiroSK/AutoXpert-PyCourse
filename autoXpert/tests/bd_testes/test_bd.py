import sqlite3
import unittest
from datetime import datetime

from tests.bd_testes.base_dados_teste import criar_conexao_teste, CAMINHO_SCHEMA


class TesteBaseDeDados(unittest.TestCase):
    # Testa o próprio schema (db/schema.sql): tabelas, chaves estrangeiras,
    # CHECKs, UNIQUE, NOT NULL e valores por defeito.
    # Cada teste começa com a base de dados de teste nova (ver base_dados_teste.py).

    def setUp(self):
        self.conexao = criar_conexao_teste()

    def tearDown(self):
        self.conexao.close()

    # Confirma que a base de dados recusa o comando
    def _deve_falhar(self, sql, parametros=()):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conexao.execute(sql, parametros)

    def _contar(self, tabela):
        return self.conexao.execute("SELECT COUNT(*) FROM " + tabela).fetchone()[0]

    def _inserir_ot(self, id_viatura=1, id_tecnico=1):
        cursor = self.conexao.execute(
            "INSERT INTO OrdemTrabalho (id_viatura, id_tecnico, data_entrada, "
            "data_prev_saida, estado, descricao_avaria) VALUES (?, ?, ?, ?, ?, ?)",
            (id_viatura, id_tecnico, "2026-10-28", "2026-10-30", "Pendente", "Avaria"))
        return cursor.lastrowid

    def _sql_linha(self):
        return ("INSERT INTO LinhaOT (id_ot, tipo, descricao, quantidade, "
                "preco_unitario, id_peca) VALUES (?, ?, ?, ?, ?, ?)")

    # ----- Tabelas -----

    def test_todas_as_tabelas_existem(self):
        cursor = self.conexao.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        tabelas = []
        for linha in cursor.fetchall():
            tabelas.append(linha[0])
        for nome in ["Cliente", "Tecnico", "Viatura", "Peca", "OrdemTrabalho",
                     "LinhaOT", "Fatura", "LogAlteracaoOT"]:
            self.assertIn(nome, tabelas)

    def test_schema_pode_ser_executado_duas_vezes(self):
        # O inicializar_bd() corre sempre que a aplicação arranca
        self.conexao.executescript(CAMINHO_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(self._contar("Viatura"), 2)

    # ----- Cliente -----

    def test_cliente_tem_data_de_registo_por_defeito(self):
        self.conexao.execute("INSERT INTO Cliente (nome) VALUES ('Maria')")
        data = self.conexao.execute(
            "SELECT data_registo FROM Cliente WHERE nome = 'Maria'").fetchone()[0]
        datetime.strptime(data, "%Y-%m-%d")  # dá erro se o formato não for AAAA-MM-DD

    def test_cliente_sem_nome_e_recusado(self):
        self._deve_falhar("INSERT INTO Cliente (nome) VALUES (NULL)")

    def test_nif_duplicado_e_recusado(self):
        self._deve_falhar("INSERT INTO Cliente (nome, NIF) VALUES ('Outro', '123456789')")

    def test_varios_clientes_sem_nif_sao_permitidos(self):
        self.conexao.execute("INSERT INTO Cliente (nome) VALUES ('A')")
        self.conexao.execute("INSERT INTO Cliente (nome) VALUES ('B')")
        self.assertEqual(self._contar("Cliente"), 3)

    def test_telefone_com_mais_de_20_caracteres_e_recusado(self):
        self._deve_falhar("INSERT INTO Cliente (nome, telefone) VALUES ('A', ?)",
                          ("9" * 21,))
        self.conexao.execute("INSERT INTO Cliente (nome, telefone) VALUES ('B', ?)",
                             ("9" * 20,))

    # ----- Viatura -----

    def test_viatura_de_cliente_inexistente_e_recusada(self):
        self._deve_falhar("INSERT INTO Viatura (matricula, marca, modelo, id_cliente) "
                          "VALUES ('EE-33-FF', 'Fiat', 'Punto', 99)")

    def test_matricula_duplicada_e_recusada(self):
        self._deve_falhar("INSERT INTO Viatura (matricula, marca, modelo, id_cliente) "
                          "VALUES ('AA-11-BB', 'Fiat', 'Punto', 1)")

    def test_quilometros_negativos_sao_recusados(self):
        self._deve_falhar("INSERT INTO Viatura (matricula, marca, modelo, km_estrada, "
                          "id_cliente) VALUES ('EE-33-FF', 'Fiat', 'Punto', -5, 1)")

    def test_quilometros_por_defeito_sao_zero(self):
        km = self.conexao.execute(
            "SELECT km_estrada FROM Viatura WHERE matricula = 'AA-11-BB'").fetchone()[0]
        self.assertEqual(km, 0)

    # ----- Técnico -----

    def test_tecnico_com_custo_hora_negativo_e_recusado(self):
        self._deve_falhar("INSERT INTO Tecnico (nome, custo_hora) VALUES ('X', -1)")

    def test_tecnico_ativo_por_defeito_e_so_aceita_0_ou_1(self):
        ativo = self.conexao.execute(
            "SELECT ativo FROM Tecnico WHERE id_tecnico = 1").fetchone()[0]
        self.assertEqual(ativo, 1)
        self._deve_falhar("INSERT INTO Tecnico (nome, custo_hora, ativo) VALUES ('X', 10, 2)")

    # ----- Peça -----

    def test_peca_com_referencia_duplicada_e_recusada(self):
        self._deve_falhar("INSERT INTO Peca (referencia, nome, preco_compra, preco_venda) "
                          "VALUES ('REF-1', 'Outra', 1, 2)")

    def test_peca_com_stock_ou_precos_negativos_e_recusada(self):
        sql = ("INSERT INTO Peca (referencia, nome, stock_atual, stock_minimo, "
               "preco_compra, preco_venda) VALUES (?, 'X', ?, ?, ?, ?)")
        self._deve_falhar(sql, ("N1", -1, 0, 1, 2))   # stock_atual negativo
        self._deve_falhar(sql, ("N2", 0, -1, 1, 2))   # stock_minimo negativo
        self._deve_falhar(sql, ("N3", 0, 0, -1, 2))   # preço de compra negativo
        self._deve_falhar(sql, ("N4", 0, 0, 1, -2))   # preço de venda negativo

    def test_stock_por_defeito_e_zero(self):
        linha = self.conexao.execute(
            "SELECT stock_atual, stock_minimo FROM Peca WHERE id_peca = 1").fetchone()
        self.assertEqual(linha[0], 0)
        self.assertEqual(linha[1], 0)

    # ----- OrdemTrabalho -----

    def test_ot_com_viatura_ou_tecnico_inexistente_e_recusada(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._inserir_ot(id_viatura=99)
        with self.assertRaises(sqlite3.IntegrityError):
            self._inserir_ot(id_tecnico=99)

    def test_ot_sem_descricao_da_avaria_e_recusada(self):
        self._deve_falhar(
            "INSERT INTO OrdemTrabalho (id_viatura, id_tecnico, data_entrada, "
            "data_prev_saida, estado, descricao_avaria) VALUES (1, 1, 'a', 'b', 'Pendente', NULL)")

    def test_ot_custo_total_por_defeito_zero_e_nao_negativo(self):
        id_ot = self._inserir_ot()
        custo = self.conexao.execute(
            "SELECT custo_total FROM OrdemTrabalho WHERE id_ot = ?", (id_ot,)).fetchone()[0]
        self.assertEqual(custo, 0)
        self._deve_falhar("UPDATE OrdemTrabalho SET custo_total = -1 WHERE id_ot = ?", (id_ot,))

    def test_ot_com_linhas_nao_pode_ser_apagada(self):
        id_ot = self._inserir_ot()
        self.conexao.execute(self._sql_linha(), (id_ot, "mao_obra", "x", 1, 10, None))
        self._deve_falhar("DELETE FROM OrdemTrabalho WHERE id_ot = ?", (id_ot,))

    # ----- LinhaOT -----

    def test_linha_com_dados_invalidos_e_recusada(self):
        id_ot = self._inserir_ot()
        sql = self._sql_linha()
        self._deve_falhar(sql, (id_ot, "outro", "x", 1, 10, None))     # tipo inválido
        self._deve_falhar(sql, (id_ot, "mao_obra", "x", 0, 10, None))  # quantidade 0
        self._deve_falhar(sql, (id_ot, "mao_obra", "x", 1, -1, None))  # preço negativo
        self._deve_falhar(sql, (99, "mao_obra", "x", 1, 10, None))     # OT inexistente
        self._deve_falhar(sql, (id_ot, "peca", "x", 1, 10, 99))        # peça inexistente
        self.assertEqual(self._contar("LinhaOT"), 0)

    def test_linha_valida_e_aceite(self):
        id_ot = self._inserir_ot()
        self.conexao.execute(self._sql_linha(), (id_ot, "peca", "Pastilhas", 2, 25, 1))
        self.assertEqual(self._contar("LinhaOT"), 1)

    # ----- Fatura -----

    def test_so_pode_haver_uma_fatura_por_ot(self):
        id_ot = self._inserir_ot()
        sql = "INSERT INTO Fatura (id_ot, data_emissao, valor_total) VALUES (?, '2026-10-30', ?)"
        self.conexao.execute(sql, (id_ot, 100))
        self._deve_falhar(sql, (id_ot, 100))

    def test_fatura_invalida_e_recusada(self):
        id_ot = self._inserir_ot()
        self._deve_falhar("INSERT INTO Fatura (id_ot, data_emissao, valor_total) "
                          "VALUES (99, '2026-10-30', 10)")           # OT inexistente
        self._deve_falhar("INSERT INTO Fatura (id_ot, data_emissao, valor_total) "
                          "VALUES (?, '2026-10-30', -1)", (id_ot,))  # valor negativo
        self._deve_falhar("INSERT INTO Fatura (id_ot, data_emissao, valor_total, pago) "
                          "VALUES (?, '2026-10-30', 10, 2)", (id_ot,))  # pago inválido

    # ----- LogAlteracaoOT -----

    def test_log_so_para_ot_existente(self):
        id_ot = self._inserir_ot()
        sql = ("INSERT INTO LogAlteracaoOT (id_ot, data_hora, campo_alterado, "
               "valor_anterior, valor_novo) VALUES (?, '2026-10-28 10:00', 'estado', ?, ?)")
        self.conexao.execute(sql, (id_ot, "Pendente", "Em Curso"))
        self.assertEqual(self._contar("LogAlteracaoOT"), 1)
        self._deve_falhar(sql, (99, "Pendente", "Em Curso"))