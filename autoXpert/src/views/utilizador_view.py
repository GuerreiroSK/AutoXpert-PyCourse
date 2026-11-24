
import tkinter as tk
from tkinter import ttk

from src.views.tema import configurar_linhas_alternadas
from src.views.estilo import (
    executar_acao,
    perguntar_sim_nao,
    PesquisaTabela,
    preparar_campo,
)


class UtilizadorView(ttk.Frame):
    # Página de gestão de utilizadores.
    # Permite criar, consultar e eliminar contas.

    def __init__(self, parent, controller):
        super().__init__(parent, padding=12)

        self.controller = controller
        self.id_selecionado = None

        self.login_var = tk.StringVar(self)
        self.senha_var = tk.StringVar(self)
        self.confirmacao_var = tk.StringVar(self)
        self.perfil_var = tk.StringVar(self, value="rececionista")
        self.estado = tk.StringVar(self, value="Criar novo utilizador.")

        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

        self.criar_formulario()
        self.criar_botoes()
        self.criar_lista()

        ttk.Label(
            self,
            textvariable=self.estado
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=8)

        self.carregar()

    # ================= Construção da página =================

    def criar_formulario(self):
        ttk.Label(
            self,
            text="Nome de utilizador *"
        ).grid(row=0, column=0, sticky="w", pady=3)

        self.entrada_login = tk.Entry(
            self,
            textvariable=self.login_var
        )
        self.entrada_login.grid(
            row=0, column=1, sticky="ew", padx=8
        )
        preparar_campo(self.entrada_login)

        ttk.Label(
            self,
            text="Palavra-passe *"
        ).grid(row=1, column=0, sticky="w", pady=3)

        self.entrada_senha = tk.Entry(
            self,
            textvariable=self.senha_var,
            show="*"
        )
        self.entrada_senha.grid(
            row=1, column=1, sticky="ew", padx=8
        )
        preparar_campo(self.entrada_senha)

        ttk.Label(
            self,
            text="Confirmar palavra-passe *"
        ).grid(row=2, column=0, sticky="w", pady=3)

        self.entrada_confirmacao = tk.Entry(
            self,
            textvariable=self.confirmacao_var,
            show="*"
        )
        self.entrada_confirmacao.grid(
            row=2, column=1, sticky="ew", padx=8
        )
        preparar_campo(self.entrada_confirmacao)

        ttk.Label(
            self,
            text="Perfil *"
        ).grid(row=3, column=0, sticky="w", pady=3)

        self.selecao_perfil = ttk.Combobox(
            self,
            textvariable=self.perfil_var,
            values=("administrador", "rececionista", "tecnico"),
            state="readonly"
        )
        self.selecao_perfil.grid(
            row=3, column=1, sticky="ew", padx=8
        )

    def criar_botoes(self):
        botoes = ttk.Frame(self)
        botoes.grid(
            row=4, column=0, columnspan=2,
            sticky="ew", pady=8
        )

        ttk.Button(
            botoes,
            text="Limpar",
            command=self.novo
        ).pack(side="left")

        ttk.Button(
            botoes,
            text="Criar utilizador",
            command=self.clicar_criar
        ).pack(side="left", padx=6)

        ttk.Button(
            botoes,
            text="Eliminar",
            style="Perigo.TButton",
            command=self.clicar_eliminar
        ).pack(side="left")


    def criar_lista(self):
        quadro = ttk.Frame(self)
        quadro.grid(
            row=5, column=0, columnspan=2,
            sticky="nsew"
        )

        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(1, weight=1)

        self.pesquisa = PesquisaTabela(
            quadro,
            self.mostrar_contagem
        )

        self.pesquisa.quadro.grid(
            row=0, column=0, columnspan=2,
            sticky="w", pady=(0, 6)
        )

        colunas = [
            ("id", "ID"),
            ("login", "Utilizador"),
            ("perfil", "Perfil"),
        ]

        nomes = [coluna[0] for coluna in colunas]

        self.lista = ttk.Treeview(
            quadro,
            columns=nomes,
            show="headings",
            selectmode="browse"
        )

        configurar_linhas_alternadas(self.lista)

        for nome, titulo in colunas:
            self.lista.heading(nome, text=titulo)
            self.lista.column(nome, width=160, minwidth=80)

        self.lista.grid(row=1, column=0, sticky="nsew")

        self.pesquisa.associar(self.lista)

        barra = ttk.Scrollbar(
            quadro,
            orient="vertical",
            command=self.lista.yview
        )
        barra.grid(row=1, column=1, sticky="ns")

        self.lista.configure(yscrollcommand=barra.set)

        self.lista.bind(
            "<<TreeviewSelect>>",
            self.ao_selecionar
        )

    # ================= Botões =================

    def clicar_criar(self):
        executar_acao(self, self.criar)

    def clicar_eliminar(self):
        executar_acao(self, self.eliminar)

    # ================= Ações =================

    def novo(self):
        self.id_selecionado = None

        self.login_var.set("")
        self.senha_var.set("")
        self.confirmacao_var.set("")
        self.perfil_var.set("rececionista")

        self.lista.selection_remove(
            self.lista.selection()
        )

        self.estado.set("Criar novo utilizador.")

    def carregar(self):
        utilizadores = self.controller.listar()

        linhas = []

        for utilizador in utilizadores:
            valores = (
                utilizador["id"],
                utilizador["login"],
                utilizador["perfil"],
            )

            linhas.append((
                str(utilizador["id"]),
                valores,
                ()
            ))

        self.pesquisa.definir_linhas(linhas)

        self.novo()

        self.mostrar_contagem(
            len(self.lista.get_children()),
            len(utilizadores)
        )

    def mostrar_contagem(self, visiveis, total):
        if self.pesquisa.pesquisa_ativa():
            self.estado.set(
                str(visiveis) + " de "
                + str(total) + " utilizador(es)."
            )
        else:
            self.estado.set(
                str(total)
                + " utilizador(es). Selecione uma linha para eliminar."
            )

    def ao_selecionar(self, evento):
        if self.lista.selection():
            self.id_selecionado = int(
                self.lista.selection()[0]
            )

            self.estado.set(
                "Utilizador selecionado: "
                + str(self.id_selecionado)
                + "."
            )

    def criar(self):
        login = self.login_var.get().strip()
        senha = self.senha_var.get()
        confirmacao = self.confirmacao_var.get()
        perfil = self.perfil_var.get()

        self.controller.criar(
            login,
            senha,
            confirmacao,
            perfil
        )

        self.carregar()

        self.estado.set(
            "Utilizador '" + login + "' criado com sucesso."
        )

    def eliminar(self):
        if self.id_selecionado is None:
            raise ValueError(
                "Selecione primeiro um utilizador na lista."
            )

        if perguntar_sim_nao(
            self,
            "Confirmar eliminação",
            "Tem a certeza de que pretende eliminar este utilizador?"
        ):
            self.controller.eliminar(self.id_selecionado)

            self.carregar()

            self.estado.set("Utilizador eliminado com sucesso.")
