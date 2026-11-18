import runpy
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import font, ttk
from unittest.mock import MagicMock, patch

from src.views.estilo import DialogoFormulario, aplicar_estilo, criar_janela
from src.views.ot_view import DialogoNovaOT
from src.views.tema import (
    aplicar_tema,
    configurar_linhas_alternadas,
    tags_linha_alternada,
)
from src.views.viatura_view import ViaturaView


class TestTema(unittest.TestCase):
    def setUp(self):
        self.raiz = tk.Tk()
        self.raiz.withdraw()
        self.addCleanup(self.raiz.destroy)
        aplicar_tema(self.raiz)
        self.estilo = ttk.Style(self.raiz)

    def test_botoes_partilham_fonte_e_texto_branco(self):
        for nome in ("TButton", "Menu.TButton", "Perigo.TButton",
                     "Menu.Perigo.TButton"):
            with self.subTest(estilo=nome):
                fonte = font.Font(
                    root=self.raiz, font=self.estilo.lookup(nome, "font"))
                self.assertEqual(fonte.cget("family"), "Calibri")
                self.assertEqual(fonte.cget("size"), 10)
                self.assertEqual(fonte.cget("weight"), "bold")
                self.assertEqual(self.estilo.lookup(nome, "foreground"), "#ffffff")

    def test_frames_e_labels_usam_fundo_consistente_e_cabecalho_14pt(self):
        for nome in ("TFrame", "TLabel", "TLabelframe", "TLabelframe.Label",
                     "Destaque.TLabel", "Rotulo.TLabel"):
            with self.subTest(estilo=nome):
                self.assertEqual(
                    self.estilo.lookup(nome, "background"), "#f2f4f7")

        self.assertEqual(
            self.estilo.lookup("Cabecalho.TLabel", "background"), "#1A3A5C")
        self.assertEqual(
            self.estilo.lookup("Cabecalho.TLabel", "foreground"), "#ffffff")
        fonte = font.Font(
            root=self.raiz,
            font=self.estilo.lookup("Cabecalho.TLabel", "font"))
        self.assertEqual(fonte.cget("size"), 14)
        self.assertEqual(fonte.cget("weight"), "bold")

    def test_treeview_tem_cabecalho_navy_e_linhas_alternadas(self):
        self.assertEqual(
            self.estilo.lookup("Treeview.Heading", "background"), "#1A3A5C")
        self.assertEqual(
            self.estilo.lookup("Treeview.Heading", "foreground"), "#ffffff")
        self.assertEqual(int(self.estilo.lookup("Treeview", "rowheight")), 26)

        tabela = ttk.Treeview(self.raiz)
        configurar_linhas_alternadas(tabela)
        tags_primeira = tags_linha_alternada(tabela)
        tabela.insert("", "end", text="linha 1", tags=tags_primeira)
        tags_segunda = tags_linha_alternada(tabela)
        tabela.insert("", "end", text="linha 2", tags=tags_segunda)
        tags_terceira = tags_linha_alternada(tabela, ("baixo",))
        tabela.insert("", "end", text="linha 3", tags=tags_terceira)

        self.assertEqual(tags_primeira, ("linha_par",))
        self.assertEqual(tags_segunda, ("linha_impar",))
        self.assertEqual(tags_terceira, ("linha_par", "baixo"))
        self.assertEqual(
            str(tabela.tag_configure("linha_par", "background")), "#ffffff")
        self.assertEqual(
            str(tabela.tag_configure("linha_impar", "background")), "#e8edf4")

    def test_janelas_e_dialogos_herdam_tema(self):
        janela = criar_janela(self.raiz, "Teste", 300, 200)
        janela.withdraw()
        secundaria = tk.Toplevel(janela)
        secundaria.withdraw()
        with patch.object(tk.Toplevel, "wait_visibility"), \
                patch.object(tk.Toplevel, "grab_set"):
            formulario = DialogoFormulario(janela, "Teste", [("nome", "Nome")])
            formulario.janela.withdraw()
            dialogo_ot = DialogoNovaOT(secundaria, MagicMock(), MagicMock())
            dialogo_ot.janela.withdraw()

        for janela_teste in (janela, secundaria, formulario.janela, dialogo_ot.janela):
            with self.subTest(janela=str(janela_teste)):
                self.assertEqual(janela_teste.cget("background"), "#f2f4f7")
                estilo = ttk.Style(janela_teste)
                self.assertEqual(estilo.theme_use(), "clam")
                self.assertEqual(estilo.lookup("TButton", "background"), "#1A3A5C")
                self.assertEqual(
                    estilo.lookup("Perigo.TButton", "background"), "#c24848")
                self.assertEqual(
                    estilo.lookup("Treeview.Heading", "background"), "#1A3A5C")

    def test_aplicar_estilo_usa_o_mesmo_tema(self):
        aplicar_estilo(self.raiz)
        self.assertEqual(self.estilo.theme_use(), "clam")
        self.assertEqual(self.estilo.lookup("TButton", "background"), "#1A3A5C")
        self.assertEqual(self.estilo.lookup("TButton", "foreground"), "#ffffff")
        fonte = font.Font(root=self.raiz, font=self.estilo.lookup("TButton", "font"))
        self.assertEqual(fonte.cget("family"), "Calibri")
        self.assertEqual(fonte.cget("size"), 10)
        self.assertEqual(fonte.cget("weight"), "bold")

    def test_arranque_aplica_tema_antes_de_criar_menu(self):
        raiz = MagicMock()
        chamadas = MagicMock()
        caminho = Path(__file__).resolve().parent.parent / "main.py"
        with patch("tkinter.Tk", return_value=raiz), \
                patch("db.connection.inicializar_bd"), \
                patch("db.connection.get_connection"), \
                patch("src.views.tema.aplicar_tema") as aplicar, \
                patch("src.views.menu_principal_view.MenuPrincipalView") as menu:
            chamadas.attach_mock(aplicar, "aplicar")
            chamadas.attach_mock(menu, "menu")
            runpy.run_path(str(caminho))

        aplicar.assert_called_once_with(raiz)
        self.assertEqual(chamadas.mock_calls[0][0], "aplicar")
        self.assertEqual(chamadas.mock_calls[1][0], "menu")

    def test_cores_distinguem_perigo_em_todos_os_estados(self):
        for nome, normal, ativa in (
            ("TButton", "#1A3A5C", "#2d527f"),
            ("Menu.TButton", "#1A3A5C", "#2d527f"),
            ("Perigo.TButton", "#c24848", "#a63c3c"),
            ("Menu.Perigo.TButton", "#c24848", "#a63c3c"),
        ):
            with self.subTest(estilo=nome):
                self.assertEqual(self.estilo.lookup(nome, "background"), normal)
                self.assertEqual(
                    self.estilo.lookup(nome, "background", ("active",)), ativa)
                self.assertEqual(
                    self.estilo.lookup(nome, "foreground", ("active",)), "#ffffff")
                self.assertEqual(
                    self.estilo.lookup(nome, "background", ("disabled", "active")),
                    "#f2f4f7")
                self.assertEqual(
                    self.estilo.lookup(nome, "foreground", ("disabled",)),
                    "#667085")
                pressionada = normal
                if "Perigo" in nome:
                    pressionada = ativa
                self.assertEqual(
                    self.estilo.lookup(nome, "background", ("pressed", "active")),
                    pressionada)

    def test_eliminar_viatura_usa_perigo_sem_mudar_comando(self):
        controller = MagicMock()
        vista = ViaturaView(self.raiz)
        vista.menu_viatura(controller)
        vista.janela.withdraw()
        corpo = vista.janela.winfo_children()[1]
        botoes = corpo.winfo_children()

        for botao in botoes:
            if botao.cget("text") == "Eliminar viatura":
                self.assertEqual(botao.cget("style"), "Menu.Perigo.TButton")
                botao.invoke()
            elif botao.cget("text") != "Fechar":
                self.assertEqual(botao.cget("style"), "Menu.TButton")

        controller.eliminar_viatura.assert_called_once_with()
