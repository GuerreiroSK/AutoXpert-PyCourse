import datetime
import sqlite3
import unittest
from unittest import mock

import bcrypt
import jwt

import auth
from tests.bd_testes.base_dados_teste import criar_conexao_vazia


class TesteAuth(unittest.TestCase):
    # Testa auth.py com a base de dados de teste (schema real, em memória)

    def setUp(self):
        self.conexao = criar_conexao_vazia()
        # rounds=4 em vez de 12 só para os testes não demorarem (o resto é igual)
        original = bcrypt.gensalt
        patcher = mock.patch("auth.bcrypt.gensalt",
                             lambda rounds=12: original(4))
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.conexao.close()

    # ----- registar_utilizador -----

    def test_guarda_hash_e_nao_a_palavra_passe(self):
        auth.registar_utilizador(self.conexao, "ana", "segredo123", "tecnico")
        guardado = self.conexao.execute(
            "SELECT senha_hash FROM utilizadores WHERE login = 'ana'").fetchone()[0]
        self.assertNotIn("segredo123", guardado)
        self.assertTrue(guardado.startswith("$2"))

    def test_mesma_palavra_passe_da_hashes_diferentes(self):
        auth.registar_utilizador(self.conexao, "a", "igual1234", "tecnico")
        auth.registar_utilizador(self.conexao, "b", "igual1234", "tecnico")
        hashes = [linha[0] for linha in
                  self.conexao.execute("SELECT senha_hash FROM utilizadores")]
        self.assertNotEqual(hashes[0], hashes[1])

    def test_perfil_invalido_e_recusado(self):
        with self.assertRaises(ValueError):
            auth.registar_utilizador(self.conexao, "ana", "segredo123", "dono")

    def test_login_repetido_e_recusado_pela_bd(self):
        auth.registar_utilizador(self.conexao, "ana", "segredo123", "tecnico")
        with self.assertRaises(sqlite3.IntegrityError):
            auth.registar_utilizador(self.conexao, "ana", "outra1234", "tecnico")

    def test_palavra_passe_demasiado_longa_e_recusada(self):
        with self.assertRaises(ValueError):
            auth.registar_utilizador(self.conexao, "ana", "x" * 73, "tecnico")

    def test_bd_recusa_perfil_fora_da_lista(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conexao.execute(
                "INSERT INTO utilizadores (login, senha_hash, perfil) "
                "VALUES ('x', 'h', 'dono')")

    # ----- autenticar -----

    def test_credenciais_certas_devolvem_login_e_perfil(self):
        auth.registar_utilizador(self.conexao, "ana", "segredo123", "rececionista")
        self.assertEqual(auth.autenticar(self.conexao, "ana", "segredo123"),
                         {"login": "ana", "perfil": "rececionista"})

    def test_palavra_passe_errada_devolve_none(self):
        auth.registar_utilizador(self.conexao, "ana", "segredo123", "tecnico")
        self.assertIsNone(auth.autenticar(self.conexao, "ana", "errada"))

    def test_utilizador_inexistente_devolve_none(self):
        self.assertIsNone(auth.autenticar(self.conexao, "ninguem", "qualquer"))

    def test_hash_guardado_como_bytes_tambem_funciona(self):
        # O PDF guarda o hash em bytes; um colega pode inserir assim
        hashed = bcrypt.hashpw(b"segredo123", bcrypt.gensalt(4))
        self.conexao.execute(
            "INSERT INTO utilizadores (login, senha_hash, perfil) VALUES (?,?,?)",
            ("rui", hashed, "tecnico"))
        self.assertIsNotNone(auth.autenticar(self.conexao, "rui", "segredo123"))

    def test_hash_corrompido_nao_deixa_entrar(self):
        self.conexao.execute(
            "INSERT INTO utilizadores (login, senha_hash, perfil) VALUES (?,?,?)",
            ("rui", "isto-nao-e-um-hash", "tecnico"))
        self.assertIsNone(auth.autenticar(self.conexao, "rui", "segredo123"))

    # ----- tokens -----

    def test_token_tem_login_perfil_e_emissor(self):
        dados = auth.validar_token(auth.criar_token("ana", "tecnico"))
        self.assertEqual(dados["sub"], "ana")
        self.assertEqual(dados["perfil"], "tecnico")
        self.assertEqual(dados["iss"], "autoxpert")

    def test_token_dura_8_horas(self):
        dados = auth.validar_token(auth.criar_token("ana", "tecnico"))
        duracao = dados["exp"] - dados["iat"]
        self.assertEqual(duracao, int(datetime.timedelta(hours=8).total_seconds()))

    def test_token_adulterado_e_recusado(self):
        token = auth.criar_token("ana", "tecnico")
        adulterado = token[:-2] + ("AA" if token[-2:] != "AA" else "BB")
        with self.assertRaises(jwt.InvalidTokenError):
            auth.validar_token(adulterado)

    def test_token_assinado_com_outra_chave_e_recusado(self):
        falso = jwt.encode({"sub": "ana", "perfil": "administrador",
                            "iss": "autoxpert"}, "outra-chave-com-32-caracteres-xx",
                           algorithm="HS256")
        with self.assertRaises(jwt.InvalidTokenError):
            auth.validar_token(falso)

    def test_token_sem_assinatura_algoritmo_none_e_recusado(self):
        falso = jwt.encode({"sub": "ana", "perfil": "administrador",
                            "iss": "autoxpert"}, None, algorithm="none")
        with self.assertRaises(jwt.InvalidTokenError):
            auth.validar_token(falso)

    def test_token_expirado_levanta_expired(self):
        passado = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=9)
        expirado = jwt.encode({"sub": "ana", "perfil": "tecnico", "iss": "autoxpert",
                               "iat": passado,
                               "exp": passado + datetime.timedelta(hours=8)},
                              auth.SECRET_KEY, algorithm="HS256")
        with self.assertRaises(jwt.ExpiredSignatureError):
            auth.validar_token(expirado)

    def test_token_de_outro_emissor_e_recusado(self):
        falso = jwt.encode({"sub": "ana", "perfil": "tecnico", "iss": "outro",
                            "exp": datetime.datetime.now(datetime.timezone.utc)
                            + datetime.timedelta(hours=1)},
                           auth.SECRET_KEY, algorithm="HS256")
        with self.assertRaises(jwt.InvalidTokenError):
            auth.validar_token(falso)

    def test_perfis_sao_os_tres_do_professor(self):
        self.assertEqual(auth.PERFIS, ["administrador", "tecnico", "rececionista"])


if __name__ == "__main__":
    unittest.main()
