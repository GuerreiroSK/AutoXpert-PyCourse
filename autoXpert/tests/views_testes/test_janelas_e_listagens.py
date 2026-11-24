import tkinter as tk
import unittest
from tkinter import ttk
from unittest.mock import patch

from src.controllers.cliente_controller import ClienteController
from src.controllers.fatura_controller import FaturaController
from src.controllers.linha_ot_controller import LinhaOTController
from src.controllers.ot_controller import OrdemTrabalhoController
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.fatura_repository import FaturaRepository
from src.repositories.linha_ot_repository import LinhaOTRepository
from src.repositories.log_alteracao_ot_repository import LogAlteracaoOTRepository
from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.services.cliente_service import ClienteService
from src.services.fatura_service import FaturaService
from src.services.linha_ot_service import LinhaOTService
from src.services.log_alteracao_ot_service import LogAlteracaoOTService
from src.services.ot_service import OrdemTrabalhoService
from src.views.cliente_view import ClienteView
from src.views.estilo import (
    ajustar_janela, criar_janela, filtrar_tabela, MARGEM_ALTURA_ECRA, MARGEM_LARGURA_ECRA
)
from src.views.fatura_view import FaturaView
from src.views.ot_view import JanelaOTs
from src.views.tema import aplicar_tema
from tests.bd_testes.base_dados_teste import criar_conexao_teste
from auth import criar_token


class BaseTk(unittest.TestCase):
    def setUp(self):
        self.raiz = tk.Tk()
        self.raiz.withdraw()
        aplicar_tema(self.raiz)
        self.addCleanup(self.raiz.destroy)
        self.conexao = criar_conexao_teste()
        self.addCleanup(self.conexao.close)
        self.token = criar_token("teste", "administrador")

    def tamanho(self, janela):
        # "LARGURAxALTURA+X+Y" -> (largura, altura). Com a janela ainda por mostrar o Tk
        # só aplica o geometry() na passagem seguinte, por isso força-se aqui.
        janela.update_idletasks()
        dimensoes = janela.geometry().split("+")[0]
        largura, altura = dimensoes.split("x")
        return int(largura), int(altura)


class TestAjustarJanela(BaseTk):

    def janela_com_conteudo(self, largura, altura):
        janela = tk.Toplevel(self.raiz)
        ttk.Frame(janela, width=largura, height=altura).pack()
        return janela

    def test_nunca_fica_mais_pequena_do_que_o_conteudo(self):
        # Era o erro das OTs: geometry 850 de altura para um conteúdo que pedia 889
        janela = self.janela_com_conteudo(400, 600)
        janela.geometry("300x200")

        ajustar_janela(janela, 300, 200)

        largura, altura = self.tamanho(janela)
        self.assertGreaterEqual(largura, 400)
        self.assertGreaterEqual(altura, 600)

    def test_mantem_o_tamanho_pedido_se_o_conteudo_for_menor(self):
        janela = self.janela_com_conteudo(100, 100)

        ajustar_janela(janela, 500, 400)

        self.assertEqual(self.tamanho(janela), (500, 400))

    def test_nunca_passa_do_tamanho_do_ecra(self):
        janela = self.janela_com_conteudo(20000, 20000)

        ajustar_janela(janela, 500, 400)

        largura, altura = self.tamanho(janela)
        self.assertLessEqual(largura, janela.winfo_screenwidth() - MARGEM_LARGURA_ECRA)
        self.assertLessEqual(altura, janela.winfo_screenheight() - MARGEM_ALTURA_ECRA)

    def test_tamanho_minimo_impede_esconder_os_botoes(self):
        janela = self.janela_com_conteudo(400, 600)

        ajustar_janela(janela, 300, 200)

        minimo = janela.minsize()
        self.assertGreaterEqual(minimo[0], 400)
        self.assertGreaterEqual(minimo[1], 600)

    def test_a_janela_fica_dentro_do_ecra(self):
        janela = self.janela_com_conteudo(400, 300)
        janela.geometry("+99999+99999")

        ajustar_janela(janela, 400, 300)

        largura, altura = self.tamanho(janela)
        _, x, y = janela.geometry().split("+")
        self.assertLessEqual(int(x) + largura, janela.winfo_screenwidth())
        self.assertLessEqual(int(y) + altura, janela.winfo_screenheight())

    def test_criar_janela_ajusta_quando_o_conteudo_esta_montado(self):
        janela = criar_janela(self.raiz, "Teste", 300, 200)
        ttk.Frame(janela, width=500, height=450).pack()

        self.raiz.update_idletasks()   # corre o after_idle de criar_janela

        largura, altura = self.tamanho(janela)
        self.assertGreaterEqual(largura, 500)
        self.assertGreaterEqual(altura, 450)

    def test_janela_fechada_antes_do_ajuste_nao_da_erro(self):
        janela = criar_janela(self.raiz, "Teste", 300, 200)
        janela.destroy()

        self.raiz.update_idletasks()   # não pode levantar TclError


class TestJanelaDasOTs(BaseTk):

    def criar(self):
        ot_repo = OrdemTrabalhoRepository(self.conexao)
        log = LogAlteracaoOTService(LogAlteracaoOTRepository(self.conexao), ot_repo)
        ot_service = OrdemTrabalhoService(ot_repo, log)
        controller = OrdemTrabalhoController(ot_service, self.token)
        linhas = LinhaOTController(
            LinhaOTService(LinhaOTRepository(self.conexao), ot_service),
            self.token
        )
        janela = tk.Toplevel(self.raiz)
        self.view = JanelaOTs(janela, controller, linhas)
        return janela

    def test_janela_das_ots_cabe_o_conteudo_ou_o_ecra(self):
        janela = self.criar()
        janela.update_idletasks()

        largura, altura = self.tamanho(janela)
        limite = janela.winfo_screenheight() - MARGEM_ALTURA_ECRA
        self.assertGreaterEqual(altura, min(janela.winfo_reqheight(), limite))

    def test_barra_de_mensagens_e_botoes_de_baixo_sao_criados_primeiro(self):
        # No pack() quem é criado primeiro com side="bottom" fica sempre visível;
        # se o ecrã for pequeno, encolhem as tabelas e não os botões
        janela = self.criar()

        filhos = janela.pack_slaves()
        barra = [f for f in filhos if f.winfo_class() == "TLabel"
                 and str(f.cget("textvariable")) == str(self.view.mensagem)][0]
        detalhe = [f for f in filhos if f.winfo_class() == "TLabelframe"
                   and str(f.cget("text")) == "OT selecionada"][0]
        self.assertLess(filhos.index(barra), filhos.index(detalhe))

    def test_botoes_de_linhas_ficam_antes_da_tabela_no_painel(self):
        janela = self.criar()
        painel = self.view.painel_linhas.quadro

        filhos = painel.pack_slaves()
        indice_tabela = filhos.index(self.view.painel_linhas.tabela)
        botoes = [f for f in filhos if f.winfo_class() == "TFrame"]
        for botao in botoes:
            self.assertLess(filhos.index(botao), indice_tabela)

    def test_custo_total_esta_na_linha_do_resumo(self):
        self.criar()

        self.assertEqual(self.view.label_custo.master, self.view.label_resumo.master)


class TestListagensComPesquisa(BaseTk):
    # Estas listagens ficavam vazias (clientes e faturas) por um erro numa fusão do
    # código: a lista era escrita na tabela mas a PesquisaTabela apagava-a logo a seguir.

    def base(self):
        self.conexao.execute("INSERT INTO Cliente (nome, NIF) VALUES ('Maria Silva', '222222222')")
        self.conexao.execute("INSERT INTO Cliente (nome, NIF) VALUES ('João Costa', '333333333')")
        self.conexao.commit()

    def test_clientes_aparecem_na_tabela(self):
        self.base()
        view = ClienteView(self.raiz, ClienteController(ClienteService(
            ClienteRepository(self.conexao)), self.token))

        view.menu()

        self.assertEqual(len(view.tabela.get_children()), 3)   # 1 do teste + 2
        self.assertIn("3 cliente(s)", view.barra.get())

    def test_clientes_sem_registos_nao_da_erro(self):
        self.conexao.execute("DELETE FROM Viatura")
        self.conexao.execute("DELETE FROM Cliente")
        self.conexao.commit()
        view = ClienteView(self.raiz, ClienteController(ClienteService(
            ClienteRepository(self.conexao)), self.token))

        view.menu()   # antes dava NameError

        self.assertEqual(len(view.tabela.get_children()), 0)
        self.assertIn("Não existem", view.barra.get())

    def test_pesquisa_de_clientes_filtra_e_repoe(self):
        self.base()
        view = ClienteView(self.raiz, ClienteController(ClienteService(
            ClienteRepository(self.conexao)), self.token))
        view.menu()

        view.pesquisa.termo.set("joao")   # sem acento e minúsculas

        self.assertEqual(len(view.tabela.get_children()), 1)
        view.pesquisa.limpar()
        self.assertEqual(len(view.tabela.get_children()), 3)

    def criar_fatura_view(self):
        ot_repo = OrdemTrabalhoRepository(self.conexao)
        ot_service = OrdemTrabalhoService(ot_repo, LogAlteracaoOTService(
            LogAlteracaoOTRepository(self.conexao), ot_repo))
        for _ in range(3):
            ot_service.criar_ot(1, 1, "2026-10-28", "2026-10-30", "Avaria")
        servico = FaturaService(FaturaRepository(self.conexao))
        for id_ot in (1, 2, 3):
            servico.registar(id_ot, 100 * id_ot, 0, None, None)
        view = FaturaView(self.raiz, FaturaController(servico, self.token))
        view.menu()
        return view

    def test_faturas_da_base_de_dados_aparecem_na_tabela(self):
        view = self.criar_fatura_view()

        self.assertEqual(len(view.tabela.get_children()), 3)
        self.assertIn("3 fatura(s)", view.barra.get())

    def test_faturas_mostram_os_valores_certos(self):
        view = self.criar_fatura_view()

        valores = view.tabela.item("2", "values")

        self.assertEqual(str(valores[1]), "2")          # OT
        self.assertEqual(str(valores[3]), "200.0")      # valor
        self.assertEqual(valores[4], "Não")             # paga

    def test_pesquisa_de_faturas(self):
        view = self.criar_fatura_view()

        view.pesquisa.termo.set("300")

        self.assertEqual(view.tabela.get_children(), ("3",))

    def test_atualizar_depois_de_gerar_nao_duplica(self):
        view = self.criar_fatura_view()

        view.listar_faturas()
        view.listar_faturas()

        self.assertEqual(len(view.tabela.get_children()), 3)

    def test_marcar_como_paga_atualiza_a_linha(self):
        view = self.criar_fatura_view()
        view.tabela.selection_set("1")
        with patch("src.views.fatura_view.pedir_dados", return_value={
                "data_pagamento": "2026-11-10", "metodo": "Dinheiro"}):
            view.marcar_paga()

        self.assertEqual(view.tabela.item("1", "values")[4], "Sim")


class TestCoresAlternadas(BaseTk):

    def tabela(self):
        tabela = ttk.Treeview(self.raiz, columns=("a",), show="headings")
        tabela.tag_configure("linha_par")
        tabela.tag_configure("linha_impar")
        return tabela

    def faixas(self, tabela):
        return [[t for t in tabela.item(i, "tags") if t.startswith("linha_")][0]
                for i in tabela.get_children()]

    def test_cores_alternam_par_impar(self):
        tabela = self.tabela()
        linhas = [(str(i), (str(i),), ()) for i in range(4)]

        filtrar_tabela(tabela, linhas, "")

        self.assertEqual(self.faixas(tabela), ["linha_par", "linha_impar", "linha_par", "linha_impar"])

    def test_depois_de_filtrar_recomeca_no_par(self):
        tabela = self.tabela()
        linhas = [(str(i), ("x" + str(i),), ()) for i in range(4)]

        filtrar_tabela(tabela, linhas, "x3")   # só sobra a 4.ª linha

        self.assertEqual(self.faixas(tabela), ["linha_par"])

    def test_mantem_as_etiquetas_da_view(self):
        tabela = self.tabela()
        tabela.tag_configure("baixo")
        linhas = [("1", ("a",), ("baixo",)), ("2", ("b",), ())]

        filtrar_tabela(tabela, linhas, "")

        self.assertIn("baixo", tabela.item("1", "tags"))
        self.assertNotIn("baixo", tabela.item("2", "tags"))


if __name__ == "__main__":
    unittest.main()
