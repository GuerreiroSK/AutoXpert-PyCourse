import tkinter as tk
import unittest
from tkinter import ttk
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.views.estilo import DialogoFormulario, COR_ERRO, COR_NORMAL, repor_cor_campo
from src.views.linha_ot_view import PainelLinhasOT
from src.views.peca_view import PecaView
from src.views.tecnico_view import TecnicoView


class Base(unittest.TestCase):
    # Estes testes criam janelas Tk (escondidas), por isso precisam de ambiente gráfico.

    def setUp(self):
        self.raiz = tk.Tk()
        self.raiz.withdraw()
        self.addCleanup(self.raiz.destroy)


class TestDialogoFormulario(Base):

    def criar(self, validar=None):
        # A janela de trás está escondida e por isso o wait_visibility() nunca
        # terminaria; o grab_set() também não é preciso nos testes.
        for nome in ("wait_visibility", "grab_set"):
            parte = patch.object(tk.Toplevel, nome, lambda *args: None)
            parte.start()
            self.addCleanup(parte.stop)
        campos = [("nome", "Nome"), ("telefone", "Telefone"), ("morada", "Morada")]
        dialogo = DialogoFormulario(self.raiz, "Teste", campos, None, "Guardar",
                                    validar, ["nome", "morada"])
        self.addCleanup(lambda: dialogo.janela.winfo_exists() and dialogo.janela.destroy())
        return dialogo

    def test_obrigatorios_vazios_nao_fecham_e_ficam_a_vermelho(self):
        dialogo = self.criar()

        with patch("src.views.estilo.messagebox.showerror") as aviso:
            dialogo.guardar()

        aviso.assert_called_once()
        mensagem = aviso.call_args[0][1]
        self.assertIn("Nome é obrigatório.", mensagem)      # todos os campos em falta
        self.assertIn("Morada é obrigatório.", mensagem)    # numa só mensagem
        self.assertNotIn("Telefone", mensagem)              # este é opcional
        self.assertEqual(str(dialogo.entradas["nome"].cget("background")), COR_ERRO)
        self.assertEqual(str(dialogo.entradas["telefone"].cget("background")), COR_NORMAL)
        self.assertIsNone(dialogo.resultado)

    def test_campo_a_vermelho_volta_ao_normal_depois_de_corrigido(self):
        dialogo = self.criar()
        with patch("src.views.estilo.messagebox.showerror"):
            dialogo.guardar()
        entrada = dialogo.entradas["nome"]

        entrada.insert(0, "Ana")
        repor_cor_campo(SimpleNamespace(widget=entrada))   # o que o FocusOut faz

        self.assertEqual(str(entrada.cget("background")), COR_NORMAL)

    def test_campos_de_texto_tem_o_focusout_ligado(self):
        dialogo = self.criar()

        self.assertNotEqual(dialogo.entradas["nome"].bind("<FocusOut>"), "")

    def test_campo_continua_a_vermelho_se_sai_vazio(self):
        dialogo = self.criar()
        with patch("src.views.estilo.messagebox.showerror"):
            dialogo.guardar()
        entrada = dialogo.entradas["nome"]

        repor_cor_campo(SimpleNamespace(widget=entrada))

        self.assertEqual(str(entrada.cget("background")), COR_ERRO)

    def test_regra_do_modulo_so_corre_depois_dos_obrigatorios(self):
        regra = MagicMock(return_value="Regra do módulo.")
        dialogo = self.criar(regra)
        with patch("src.views.estilo.messagebox.showerror"):
            dialogo.guardar()
        regra.assert_not_called()

        dialogo.entradas["nome"].insert(0, "Ana")
        dialogo.entradas["morada"].insert(0, "Rua X")
        with patch("src.views.estilo.messagebox.showerror") as aviso:
            dialogo.guardar()

        regra.assert_called_once()
        self.assertEqual(aviso.call_args[0][1], "Regra do módulo.")

    def test_tudo_certo_devolve_os_dados(self):
        dialogo = self.criar()
        dialogo.entradas["nome"].insert(0, " Ana ")
        dialogo.entradas["morada"].insert(0, "Rua X")

        dialogo.guardar()

        self.assertEqual(dialogo.resultado,
                         {"nome": "Ana", "telefone": "", "morada": "Rua X"})


class TestTecnicoView(Base):

    def setUp(self):
        super().setUp()
        self.controller = MagicMock()
        self.controller.listar.return_value = []
        self.pagina = TecnicoView(self.raiz, self.controller)

    def test_campos_vazios_nao_chamam_o_controller_e_ficam_a_vermelho(self):
        self.pagina.campos["custo_hora"].set("")

        with self.assertRaises(ValueError) as erro:
            self.pagina.guardar()

        self.controller.guardar.assert_not_called()
        self.assertIn("Nome é obrigatório.", str(erro.exception))
        self.assertEqual(str(self.pagina.entradas["nome"].cget("background")), COR_ERRO)
        self.assertEqual(str(self.pagina.entradas["custo_hora"].cget("background")), COR_ERRO)

    def test_custo_com_letras_ou_negativo(self):
        self.pagina.campos["nome"].set("Ana")
        for valor in ("vinte", "-5"):
            self.pagina.campos["custo_hora"].set(valor)
            with self.assertRaises(ValueError):
                self.pagina.guardar()
        self.controller.guardar.assert_not_called()

    def test_botao_guardar_mostra_aviso_sem_rebentar(self):
        with patch("src.views.estilo.messagebox.showerror") as aviso:
            self.pagina.clicar_guardar()

        aviso.assert_called_once()


class TestPecaView(Base):

    def setUp(self):
        super().setUp()
        self.controller = MagicMock()
        self.controller.listar.return_value = []
        self.pagina = PecaView(self.raiz, self.controller)

    def test_campos_vazios_nao_chamam_o_controller(self):
        with self.assertRaises(ValueError) as erro:
            self.pagina.guardar()

        self.controller.guardar.assert_not_called()
        self.assertIn("Referência é obrigatório.", str(erro.exception))
        self.assertEqual(str(self.pagina.entradas["referencia"].cget("background")), COR_ERRO)

    def test_precos_invalidos_e_negativos(self):
        self.pagina.campos["referencia"].set("R1")
        self.pagina.campos["nome"].set("Filtro")
        self.pagina.campos["preco_compra"].set("abc")
        self.pagina.campos["preco_venda"].set("-3")
        self.pagina.campos["stock_atual"].set("1")
        self.pagina.campos["stock_minimo"].set("1")

        with self.assertRaises(ValueError) as erro:
            self.pagina.guardar()

        mensagem = str(erro.exception)
        self.assertIn("Preço de compra", mensagem)
        self.assertIn("Preço de venda não pode ser negativo", mensagem)
        self.assertEqual(str(self.pagina.entradas["preco_compra"].cget("background")), COR_ERRO)
        self.assertEqual(str(self.pagina.entradas["preco_venda"].cget("background")), COR_ERRO)
        self.assertEqual(str(self.pagina.entradas["nome"].cget("background")), COR_NORMAL)

    def test_ajustar_stock_com_letras(self):
        self.pagina.movimento.set("abc")

        with self.assertRaises(ValueError):
            self.pagina.ajustar_stock()


class TestLinhasOTView(Base):

    def test_campos_sao_tk_entry_para_o_vermelho_aparecer(self):
        # O ttk.Entry ignora background=, por isso estes campos têm de ser tk.Entry
        painel = PainelLinhasOT(self.raiz, MagicMock(), MagicMock())

        for campo in (painel.entrada_descricao, painel.entrada_quantidade,
                      painel.entrada_preco, painel.entrada_horas, painel.entrada_peca):
            self.assertIsInstance(campo, tk.Entry)
            self.assertNotIsInstance(campo, ttk.Entry)

    def test_adicionar_linha_invalida_nao_chama_o_controller(self):
        controller = MagicMock()
        painel = PainelLinhasOT(self.raiz, controller, MagicMock())
        painel.id_ot_atual = 1

        with patch("src.views.linha_ot_view.mostrar_erro") as aviso:
            painel.adicionar_linha()

        aviso.assert_called_once()
        controller.adicionar_linha.assert_not_called()
        self.assertEqual(str(painel.entrada_descricao.cget("background")), COR_ERRO)


if __name__ == "__main__":
    unittest.main()
