import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# Simula auth.py enquanto ainda está a ser desenvolvido.
if "auth" not in sys.modules:
    auth_falso = types.ModuleType("auth")
    auth_falso.validar_token = None
    sys.modules["auth"] = auth_falso

from src.controllers.fatura_controller import FaturaController


class TestFaturaController(unittest.TestCase):

    def setUp(self):
        self.servico = MagicMock()
        self.controller = FaturaController(
            self.servico,
            token="token_teste"
        )

    # --------------------------------------------------
    # Testes de acesso do administrador
    # --------------------------------------------------

    @patch("src.rbac.validar_token")
    def test_administrador_tem_acesso_a_todas_as_operacoes(self, mock_validar):
        mock_validar.return_value = {"perfil": "administrador"}

        self.controller.registar_fatura(1, 100, False, None, None)
        self.controller.gerar_fatura_por_ot(1)
        self.controller.listar_faturas()
        self.controller.consultar_fatura(1)
        self.controller.consultar_detalhe(1)
        self.controller.atualizar_fatura("fatura")
        self.controller.marcar_fatura_como_paga(1, "2026-11-20", "Dinheiro")
        self.controller.eliminar_fatura(1)
        self.controller.exportar_relatorio_mensal(11, 2026)

        self.servico.registar.assert_called_once_with(
            1, 100, False, None, None
        )
        self.servico.gerar_por_ot.assert_called_once_with(1)
        self.servico.listar_todos.assert_called_once()
        self.servico.obter_por_id.assert_called_once_with(1)
        self.servico.obter_detalhe.assert_called_once_with(1)
        self.servico.atualizar.assert_called_once_with("fatura")
        self.servico.marcar_como_paga.assert_called_once_with(
            1, "2026-11-20", "Dinheiro"
        )
        self.servico.eliminar.assert_called_once_with(1)
        self.servico.exportar_relatorio_mensal.assert_called_once_with(
            11, 2026
        )

    # --------------------------------------------------
    # Testes de acesso do rececionista
    # --------------------------------------------------

    @patch("src.rbac.validar_token")
    def test_rececionista_tem_acesso_a_operacoes_permitidas(self, mock_validar):
        mock_validar.return_value = {"perfil": "rececionista"}

        self.controller.registar_fatura(1, 100, False, None, None)
        self.controller.gerar_fatura_por_ot(1)
        self.controller.listar_faturas()
        self.controller.consultar_fatura(1)
        self.controller.consultar_detalhe(1)

        self.controller.atualizar_fatura("fatura")
        self.controller.marcar_fatura_como_paga(1, "2026-11-20", "Dinheiro")
        self.controller.eliminar_fatura(1)
        self.controller.exportar_relatorio_mensal(11, 2026)

        self.servico.atualizar.assert_called_once_with("fatura")
        self.servico.marcar_como_paga.assert_called_once_with(
            1, "2026-11-20", "Dinheiro"
        )
        self.servico.eliminar.assert_called_once_with(1)
        self.servico.exportar_relatorio_mensal.assert_called_once_with(11, 2026)

        self.servico.registar.assert_called_once()
        self.servico.gerar_por_ot.assert_called_once_with(1)
        self.servico.listar_todos.assert_called_once()
        self.servico.obter_por_id.assert_called_once_with(1)
        self.servico.obter_detalhe.assert_called_once_with(1)

    # --------------------------------------------------
    # Testes de acesso do técnico
    # --------------------------------------------------

    @patch("src.rbac.validar_token")
    def test_tecnico_nao_tem_acesso_a_faturas(self, mock_validar):
        mock_validar.return_value = {"perfil": "tecnico"}

        operacoes = [
            lambda: self.controller.registar_fatura(
                1, 100, False, None, None
            ),
            lambda: self.controller.gerar_fatura_por_ot(1),
            lambda: self.controller.listar_faturas(),
            lambda: self.controller.consultar_fatura(1),
            lambda: self.controller.consultar_detalhe(1),
            lambda: self.controller.atualizar_fatura("fatura"),
            lambda: self.controller.marcar_fatura_como_paga(
                1, "2026-11-20", "Dinheiro"
            ),
            lambda: self.controller.eliminar_fatura(1),
            lambda: self.controller.exportar_relatorio_mensal(11, 2026),
        ]

        for operacao in operacoes:
            with self.subTest(operacao=operacao):
                with self.assertRaises(PermissionError):
                    operacao()

        # Nenhuma operação deve chegar ao serviço.
        for chamada in vars(self.servico).values():
            if hasattr(chamada, "assert_not_called"):
                chamada.assert_not_called()


if __name__ == "__main__":
    unittest.main()
