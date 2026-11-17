import tkinter as tk
import unittest
from tkinter import ttk
from unittest.mock import MagicMock

from src.models.cliente_model import Cliente
from src.models.tecnico_model import Tecnico
from src.views.cliente_view import ClienteView
from src.views.estilo import normalizar, filtrar_tabela, PesquisaTabela
from src.views.tecnico_view import TecnicoView


def nomes_na_tabela(tabela):
    # Segunda coluna (o nome) de cada linha visível, pela ordem em que aparece
    nomes = []
    for item in tabela.get_children():
        nomes.append(tabela.item(item, "values")[1])
    return nomes


class TestNormalizar(unittest.TestCase):

    def test_minusculas_e_sem_acentos(self):
        self.assertEqual(normalizar("JOÃO Conceição"), "joao conceicao")

    def test_numeros_viram_texto(self):
        self.assertEqual(normalizar(12.5), "12.5")


class TestPesquisaTabela(unittest.TestCase):
    # Abrem uma janela Tk (escondida), por isso precisam de ambiente gráfico.

    def setUp(self):
        self.janela = tk.Tk()
        self.janela.withdraw()
        self.addCleanup(self.janela.destroy)

        self.tabela = ttk.Treeview(self.janela, columns=("id", "nome", "estado"),
                                   show="headings")
        self.tabela.tag_configure("baixo", background="#fff2cc")
        self.linhas = [
            ("1", (1, "Ana Ferreira", "Ativo"), ()),
            ("2", (2, "João Pires", "Ativo"), ("baixo",)),
            ("3", (3, "Joana Dias", "Inativo"), ()),
        ]
        self.chamadas = []
        self.pesquisa = PesquisaTabela(self.janela, self.guardar_chamada)
        self.pesquisa.associar(self.tabela)

    def guardar_chamada(self, visiveis, total):
        self.chamadas.append((visiveis, total))

    def test_filtrar_tabela_devolve_quantas_linhas_ficaram(self):
        visiveis = filtrar_tabela(self.tabela, self.linhas, "jo")

        self.assertEqual(visiveis, 2)
        self.assertEqual(nomes_na_tabela(self.tabela), ["João Pires", "Joana Dias"])

    def test_filtrar_ignora_maiusculas_e_acentos(self):
        filtrar_tabela(self.tabela, self.linhas, "JOAO")

        # "joao" (sem til, em maiúsculas) encontra "João", mas não "Joana"
        self.assertEqual(nomes_na_tabela(self.tabela), ["João Pires"])

    def test_filtrar_procura_em_todas_as_colunas(self):
        filtrar_tabela(self.tabela, self.linhas, "inativo")

        self.assertEqual(nomes_na_tabela(self.tabela), ["Joana Dias"])

    def test_filtrar_sem_resultados_deixa_a_tabela_vazia(self):
        self.assertEqual(filtrar_tabela(self.tabela, self.linhas, "xyz"), 0)
        self.assertEqual(len(self.tabela.get_children()), 0)

    def test_escrever_filtra_em_tempo_real(self):
        self.pesquisa.definir_linhas(self.linhas)

        self.pesquisa.termo.set("ana f")

        self.assertEqual(nomes_na_tabela(self.tabela), ["Ana Ferreira"])
        self.assertEqual(self.chamadas[-1], (1, 3))

    def test_limpar_repoe_a_lista_completa(self):
        self.pesquisa.definir_linhas(self.linhas)
        self.pesquisa.termo.set("ana")

        self.pesquisa.limpar()

        self.assertEqual(len(self.tabela.get_children()), 3)
        self.assertFalse(self.pesquisa.pesquisa_ativa())
        # a lista original nunca foi alterada
        self.assertEqual(len(self.linhas), 3)
        self.assertEqual(len(self.pesquisa.linhas), 3)

    def test_etiquetas_de_cor_mantem_se_ao_repor(self):
        self.pesquisa.definir_linhas(self.linhas)
        self.pesquisa.termo.set("pires")
        self.pesquisa.limpar()

        self.assertEqual(self.tabela.item("2", "tags"), ("baixo",))

    def test_recarregar_mantem_a_pesquisa_ativa(self):
        self.pesquisa.definir_linhas(self.linhas)
        self.pesquisa.termo.set("ferreira")

        self.pesquisa.definir_linhas(self.linhas)

        self.assertEqual(nomes_na_tabela(self.tabela), ["Ana Ferreira"])

    def test_atualizar_linha_muda_tabela_e_lista_guardada(self):
        self.pesquisa.definir_linhas(self.linhas)
        self.pesquisa.termo.set("ana")

        self.pesquisa.atualizar_linha("1", (1, "Ana Ferreira", "Inativo"))
        self.assertEqual(self.tabela.item("1", "values")[2], "Inativo")

        # depois de limpar a pesquisa, o valor novo continua lá (não voltou o antigo)
        self.pesquisa.limpar()
        self.assertEqual(self.tabela.item("1", "values")[2], "Inativo")

    def test_linhas_sem_iid_sao_aceites(self):
        linhas = [(None, (1, "Ana", "Ativo"), ()), (None, (2, "Rui", "Ativo"), ())]

        self.assertEqual(filtrar_tabela(self.tabela, linhas, "rui"), 1)


class TestPesquisaNasViews(unittest.TestCase):

    def setUp(self):
        self.janela = tk.Tk()
        self.janela.withdraw()
        self.addCleanup(self.janela.destroy)

    def test_clientes_filtra_e_mostra_a_contagem(self):
        controller = MagicMock()
        controller.listar_clientes.return_value = [
            Cliente("Ana Ferreira", "100000001", None, None, None, "2026-01-01", 1),
            Cliente("Rui Carvalho", "100000002", None, None, None, "2026-01-01", 2),
        ]
        vista = ClienteView(self.janela, controller)
        vista.menu()
        self.addCleanup(vista.janela.destroy)

        vista.pesquisa.termo.set("rui")

        self.assertEqual(nomes_na_tabela(vista.tabela), ["Rui Carvalho"])
        self.assertEqual(vista.barra.get(), "1 de 2 cliente(s)")

        vista.pesquisa.limpar()

        self.assertEqual(vista.barra.get(), "2 cliente(s)")

    def test_tecnicos_filtra_por_especialidade(self):
        controller = MagicMock()
        controller.listar.return_value = [
            Tecnico("João Pires", "Motor", 28.0, True, 1),
            Tecnico("Sofia Lopes", "Eletrónica", 30.0, True, 2),
        ]
        pagina = TecnicoView(self.janela, controller)

        pagina.pesquisa.termo.set("eletronica")

        self.assertEqual(nomes_na_tabela(pagina.lista), ["Sofia Lopes"])
        self.assertEqual(pagina.estado.get(), "1 de 2 técnico(s).")