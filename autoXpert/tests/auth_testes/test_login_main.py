import runpy
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

CAMINHO_MAIN = Path(__file__).resolve().parents[2] / "main.py"


class TesteLoginNoMain(unittest.TestCase):
    # Testa o fluxo de login do main.py sem abrir janelas reais: os diálogos
    # (simpledialog/messagebox) e o menu são substituídos por simulações.

    def correr_main(self, respostas, autenticar):
        raiz = MagicMock()
        ligacao = MagicMock()
        ligacao.execute.return_value.fetchone.return_value = [1]  # já há utilizadores
        with patch("tkinter.Tk", return_value=raiz), \
                patch("db.connection.inicializar_bd"), \
                patch("db.connection.get_connection", return_value=ligacao), \
                patch("src.views.tema.aplicar_tema"), \
                patch("tkinter.simpledialog.askstring", side_effect=respostas), \
                patch("tkinter.messagebox.showerror") as erro, \
                patch("auth.autenticar", side_effect=autenticar) as aut, \
                patch("src.views.menu_principal_view.MenuPrincipalView") as menu:
            runpy.run_path(str(CAMINHO_MAIN))
        return raiz, erro, aut, menu

    def test_login_certo_abre_o_menu(self):
        raiz, erro, aut, menu = self.correr_main(
            ["ana", "segredo"], [{"login": "ana", "perfil": "tecnico"}])
        menu.assert_called_once()
        raiz.deiconify.assert_called_once()
        erro.assert_not_called()

    def test_cancelar_o_login_fecha_sem_erro(self):
        raiz, erro, aut, menu = self.correr_main([None], [])
        menu.assert_not_called()
        raiz.destroy.assert_called_once()
        erro.assert_not_called()
        aut.assert_not_called()

    def test_cancelar_na_palavra_passe_fecha_sem_erro(self):
        raiz, erro, aut, menu = self.correr_main(["ana", None], [])
        menu.assert_not_called()
        erro.assert_not_called()

    def test_errar_uma_vez_permite_tentar_outra(self):
        raiz, erro, aut, menu = self.correr_main(
            ["ana", "errada", "ana", "certa"],
            [None, {"login": "ana", "perfil": "tecnico"}])
        self.assertEqual(erro.call_count, 1)
        menu.assert_called_once()

    def test_tres_falhas_fecham_a_aplicacao(self):
        raiz, erro, aut, menu = self.correr_main(
            ["a", "x", "a", "x", "a", "x"], [None, None, None])
        self.assertEqual(erro.call_count, 3)
        menu.assert_not_called()
        raiz.destroy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
