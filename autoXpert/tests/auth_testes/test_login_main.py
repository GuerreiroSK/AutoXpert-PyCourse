import runpy
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

CAMINHO_MAIN = Path(__file__).resolve().parents[2] / "main.py"


class TesteLoginNoMain(unittest.TestCase):
    # Testa o fluxo de login do main.py sem abrir janelas reais: os diálogos
    # (simpledialog/messagebox) e o menu são substituídos por simulações.

    
    def correr_main(self, submissao, respostas_autenticacao):
        raiz = MagicMock()
        ligacao = MagicMock()
        ligacao.execute.return_value.fetchone.return_value = [1]

        autenticacao = MagicMock()
        aplicacao = MagicMock()

        def criar_autenticacao(raiz, primeiro_acesso, ao_submeter):
            autenticacao.ao_submeter = ao_submeter
            autenticacao.primeiro_acesso = primeiro_acesso
            return autenticacao

        # Simula o preenchimento e envio do formulário.
        raiz.mainloop.side_effect = lambda: submissao(
            autenticacao.ao_submeter
        )

        with patch("tkinter.Tk", return_value=raiz), \
                patch("db.connection.inicializar_bd"), \
                patch("db.connection.get_connection", return_value=ligacao), \
                patch("src.views.tema.aplicar_tema"), \
                patch("src.views.autenticacao_view.ajustar_janela"), \
                patch(
                    "src.views.autenticacao_view.AutenticacaoView",
                    side_effect=criar_autenticacao
                ), \
                patch(
                    "auth.autenticar",
                    side_effect=respostas_autenticacao
                ) as aut, \
                patch("tkinter.messagebox.showerror") as erro:

            # Carrega o main.py sem arrancar automaticamente a aplicação.
            namespace = runpy.run_path(
                str(CAMINHO_MAIN),
                run_name="autoxpert_test"
            )

            # Substitui a classe real por uma simulação.
            namespace["main"].__globals__["AplicacaoAutoXpert"] = aplicacao

            # Executa o fluxo principal.
            namespace["main"]()

        return raiz, erro, aut, aplicacao, autenticacao


    def test_login_certo_abre_a_aplicacao(self):
        utilizador = {"login": "ana", "perfil": "tecnico"}

        raiz, erro, aut, aplicacao, autenticacao = self.correr_main(
            lambda submeter: submeter("ana", "segredo", None),
            [utilizador]
        )

        aut.assert_called_once()
        aplicacao.assert_called_once()
        raiz.deiconify.assert_called_once()
        erro.assert_not_called()

    def test_campos_vazios_nao_tentam_autenticar(self):
        raiz, erro, aut, aplicacao, autenticacao = self.correr_main(
            lambda submeter: submeter("", "", None),
            []
        )

        aut.assert_not_called()
        aplicacao.assert_not_called()
        autenticacao.mostrar_mensagem.assert_called_once_with(
            "Preencha todos os campos."
        )
        erro.assert_not_called()

    def test_erro_uma_vez_permite_tentar_outra(self):
        utilizador = {"login": "ana", "perfil": "tecnico"}

        def submissoes(submeter):
            submeter("ana", "errada", None)
            submeter("ana", "certa", None)

        raiz, erro, aut, aplicacao, autenticacao = self.correr_main(
            submissoes,
            [None, utilizador]
        )

        self.assertEqual(aut.call_count, 2)
        self.assertEqual(autenticacao.mostrar_mensagem.call_count, 1)
        autenticacao.limpar_campos.assert_called_once()
        aplicacao.assert_called_once()
        erro.assert_not_called()

    def test_tres_falhas_fecham_a_aplicacao(self):
        def submissoes(submeter):
            submeter("ana", "errada", None)
            submeter("ana", "errada", None)
            submeter("ana", "errada", None)

        raiz, erro, aut, aplicacao, autenticacao = self.correr_main(
            submissoes,
            [None, None, None]
        )

        self.assertEqual(aut.call_count, 3)
        erro.assert_called_once()
        raiz.destroy.assert_called_once()
        aplicacao.assert_not_called()

if __name__ == "__main__":
    unittest.main()
