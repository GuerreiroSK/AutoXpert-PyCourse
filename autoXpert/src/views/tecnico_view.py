import tkinter as tk
from tkinter import messagebox, ttk

from src.controllers.tecnico_controller import TecnicoController
from src.views.mensagens import executar_acao


class TecnicoView(ttk.Frame):
    def __init__(self, parent: tk.Misc, controller: TecnicoController):
        super().__init__(parent, padding=12)
        self.controller = controller
        self.id_selecionado: int | None = None
        self.campos = {
            "nome": tk.StringVar(self),
            "especialidade": tk.StringVar(self),
            "custo_hora": tk.StringVar(self, value="0"),
        }
        self.ativo = tk.BooleanVar(self, value=True)
        self.apenas_ativos = tk.BooleanVar(self, value=False)
        self.estado = tk.StringVar(self, value="Novo tecnico.")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

        for linha, (chave, rotulo) in enumerate((
            ("nome", "Nome *"), ("especialidade", "Especialidade"),
            ("custo_hora", "Custo/hora (EUR) *"),
        )):
            ttk.Label(self, text=rotulo).grid(row=linha, column=0, sticky="w", pady=3)
            ttk.Entry(self, textvariable=self.campos[chave]).grid(
                row=linha, column=1, sticky="ew", padx=8
            )
        ttk.Checkbutton(self, text="Ativo", variable=self.ativo).grid(row=3, column=1, sticky="w")

        botoes = ttk.Frame(self)
        botoes.grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Button(botoes, text="Novo", command=self.novo).pack(side="left")
        ttk.Button(
            botoes, text="Guardar", command=lambda: executar_acao(self, self.guardar)
        ).pack(side="left", padx=6)
        ttk.Button(
            botoes, text="Eliminar", command=lambda: executar_acao(self, self.eliminar)
        ).pack(side="left")
        ttk.Button(
            botoes, text="Atualizar lista",
            command=lambda: executar_acao(self, self.carregar),
        ).pack(side="left", padx=6)
        ttk.Checkbutton(
            botoes, text="Apenas ativos", variable=self.apenas_ativos,
            command=lambda: executar_acao(self, self.carregar),
        ).pack(side="left")

        tabela = ttk.Frame(self)
        tabela.grid(row=5, column=0, columnspan=2, sticky="nsew")
        tabela.columnconfigure(0, weight=1)
        tabela.rowconfigure(0, weight=1)
        colunas = ("id", "nome", "especialidade", "custo_hora", "ativo")
        self.lista = ttk.Treeview(tabela, columns=colunas, show="headings", selectmode="browse")
        for coluna, rotulo in zip(
            colunas, ("ID", "Nome", "Especialidade", "Custo/hora (EUR)", "Ativo")
        ):
            self.lista.heading(coluna, text=rotulo)
            self.lista.column(coluna, width=140, minwidth=60)
        self.lista.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(tabela, orient="vertical", command=self.lista.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.lista.configure(yscrollcommand=scroll.set)
        self.lista.bind("<<TreeviewSelect>>", self.ao_selecionar)
        ttk.Label(self, textvariable=self.estado).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=8
        )
        self.carregar()

    def novo(self) -> None:
        self.id_selecionado = None
        for chave, variavel in self.campos.items():
            variavel.set("0" if chave == "custo_hora" else "")
        self.ativo.set(True)
        self.lista.selection_remove(self.lista.selection())
        self.estado.set("Novo tecnico. Preencha os campos e clique em Guardar.")

    def carregar(self) -> None:
        tecnicos = self.controller.listar(self.apenas_ativos.get())
        self.lista.delete(*self.lista.get_children())
        for tecnico in tecnicos:
            self.lista.insert("", "end", iid=str(tecnico.id_tecnico), values=(
                tecnico.id_tecnico, tecnico.nome, tecnico.especialidade or "",
                f"{tecnico.custo_hora:.2f}", "Sim" if tecnico.ativo else "Nao",
            ))
        self.novo()
        self.estado.set(f"{len(tecnicos)} tecnico(s). Selecione uma linha para editar.")

    def ao_selecionar(self, evento: tk.Event) -> None:
        if self.lista.selection():
            executar_acao(self, self.preencher_selecao)

    def preencher_selecao(self) -> None:
        tecnico = self.controller.obter(int(self.lista.selection()[0]))
        self.id_selecionado = tecnico.id_tecnico
        self.campos["nome"].set(tecnico.nome)
        self.campos["especialidade"].set(tecnico.especialidade or "")
        self.campos["custo_hora"].set(str(tecnico.custo_hora))
        self.ativo.set(tecnico.ativo)
        self.estado.set(f"A editar o tecnico {tecnico.id_tecnico}.")

    def guardar(self) -> None:
        dados = {chave: variavel.get() for chave, variavel in self.campos.items()}
        tecnico = self.controller.guardar(dados, self.ativo.get(), self.id_selecionado)
        self.carregar()
        self.estado.set(f"Tecnico {tecnico.id_tecnico} guardado.")

    def eliminar(self) -> None:
        if self.id_selecionado is None:
            raise ValueError("Selecione primeiro um tecnico na lista.")
        if messagebox.askyesno(
            "Confirmar", "Eliminar o tecnico selecionado?", parent=self
        ):
            self.controller.eliminar(self.id_selecionado)
            self.carregar()
            self.estado.set("Tecnico eliminado.")
