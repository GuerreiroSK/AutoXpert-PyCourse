
import sys
import types
import unittest
from unittest.mock import patch

import jwt


# Simula o módulo auth.py, que ainda está a ser desenvolvido.
auth_falso = types.ModuleType("auth")
auth_falso.validar_token = None
sys.modules["auth"] = auth_falso

from src.rbac import obter_perfil, require_perfil


class ControllerTeste:

    def __init__(self, token=None):
        self.token = token

    @require_perfil("administrador")
    def operacao_admin(self):
        return "Operação executada"

    @require_perfil("administrador", "rececionista")
    def operacao_recepcao(self):
        return "Operação executada"

    @require_perfil("administrador", "tecnico", "rececionista")
    def operacao_todos(self):
        return "Operação executada"


class TestRBAC(unittest.TestCase):

    def setUp(self):
        self.controller = ControllerTeste(token="token_teste")

    @patch("src.rbac.validar_token")
    def test_administrador_tem_acesso(self, mock_validar):
        mock_validar.return_value = {"perfil": "administrador"}

        resultado = self.controller.operacao_admin()

        self.assertEqual(resultado, "Operação executada")

    @patch("src.rbac.validar_token")
    def test_rececionista_tem_acesso_a_operacao_autorizada(self, mock_validar):
        mock_validar.return_value = {"perfil": "rececionista"}

        resultado = self.controller.operacao_recepcao()

        self.assertEqual(resultado, "Operação executada")

    @patch("src.rbac.validar_token")
    def test_tecnico_tem_acesso_a_operacao_autorizada(self, mock_validar):
        mock_validar.return_value = {"perfil": "tecnico"}

        resultado = self.controller.operacao_todos()

        self.assertEqual(resultado, "Operação executada")

    @patch("src.rbac.validar_token")
    def test_tecnico_nao_tem_acesso_a_operacao_admin(self, mock_validar):
        mock_validar.return_value = {"perfil": "tecnico"}

        with self.assertRaises(PermissionError):
            self.controller.operacao_admin()

    @patch("src.rbac.validar_token")
    def test_rececionista_nao_tem_acesso_a_operacao_admin(self, mock_validar):
        mock_validar.return_value = {"perfil": "rececionista"}

        with self.assertRaises(PermissionError):
            self.controller.operacao_admin()

    def test_token_ausente(self):
        controller = ControllerTeste()

        with self.assertRaises(PermissionError):
            controller.operacao_admin()

    @patch("src.rbac.validar_token")
    def test_token_invalido(self, mock_validar):
        mock_validar.side_effect = jwt.InvalidTokenError()

        with self.assertRaises(PermissionError):
            self.controller.operacao_admin()

    @patch("src.rbac.validar_token")
    def test_sessao_expirada(self, mock_validar):
        mock_validar.side_effect = jwt.ExpiredSignatureError()

        with self.assertRaisesRegex(PermissionError, "Sessão expirada"):
            self.controller.operacao_admin()

    @patch("src.rbac.validar_token")
    def test_obter_perfil_devolve_perfil(self, mock_validar):
        mock_validar.return_value = {"perfil": "administrador"}

        resultado = obter_perfil("token_teste")

        self.assertEqual(resultado, "administrador")


if __name__ == "__main__":
    unittest.main()
