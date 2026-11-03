import tkinter as tk
from tkinter import ttk

from src.views.estilo import executar_acao, perguntar_sim_nao


class TecnicoView(ttk.Frame):
    # Página de gestão de técnicos: formulário em cima, lista em baixo.
    # Só desenha e recolhe dados; o resto é pedido ao TecnicoController.

    def __init__(self, parent, controller):
        super().__init__(parent, padding=12)
        self.controller = controller
        self.id_selecionado = None  # técnico que está a ser editado (None = novo)
        self.campos = {
            "nome": tk.StringVar(self),
            "especialidade": tk.StringVar(self),
            "custo_hora": tk.StringVar(self, value="0"),
        }
        self.ativo = tk.BooleanVar(self, value=True)
        self.apenas_ativos = tk.BooleanVar(self, value=False)
        self.estado = tk.StringVar(self, value="Novo técnico.")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

        self.criar_formulario()
        self.criar_botoes()
        self.criar_lista()
        ttk.Label(self, textvariable=self.estado).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=8)

        self.carregar()

    # ================= Construção da janela =================

    def criar_formulario(self):
        rotulos = [("nome", "Nome *"), ("especialidade", "Especialidade"),
                   ("custo_hora", "Custo/hora (€) *")]
        linha = 0
        for chave, rotulo in rotulos:
            ttk.Label(self, text=rotulo).grid(row=linha, column=0, sticky="w", pady=3)
            ttk.Entry(self, textvariable=self.campos[chave]).grid(
                row=linha, column=1, sticky="ew", padx=8)
            linha += 1
        ttk.Checkbutton(self, text="Ativo", variable=self.ativo).grid(
            row=3, column=1, sticky="w")

    def criar_botoes(self):
        botoes = ttk.Frame(self)
        botoes.grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Button(botoes, text="Novo", command=self.novo).pack(side="left")
        ttk.Button(botoes, text="Guardar",
                   command=self.clicar_guardar).pack(side="left", padx=6)
        ttk.Button(botoes, text="Eliminar",
                   command=self.clicar_eliminar).pack(side="left")
        ttk.Button(botoes, text="Atualizar lista",
                   command=self.clicar_atualizar).pack(side="left", padx=6)
        ttk.Checkbutton(botoes, text="Apenas ativos", variable=self.apenas_ativos,
                        command=self.clicar_atualizar).pack(side="left")

    def criar_lista(self):
        quadro = ttk.Frame(self)
        quadro.grid(row=5, column=0, columnspan=2, sticky="nsew")
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)

        colunas = [("id", "ID"), ("nome", "Nome"), ("especialidade", "Especialidade"),
                   ("custo_hora", "Custo/hora (€)"), ("ativo", "Ativo")]
        nomes = []
        for coluna in colunas:
            nomes.append(coluna[0])

        self.lista = ttk.Treeview(quadro, columns=nomes, show="headings",
                                  selectmode="browse")
        for nome, titulo in colunas:
            self.lista.heading(nome, text=titulo)
            self.lista.column(nome, width=140, minwidth=60)
        self.lista.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(quadro, orient="vertical", command=self.lista.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.lista.configure(yscrollcommand=barra.set)
        self.lista.bind("<<TreeviewSelect>>", self.ao_selecionar)

    # ================= Botões (mostram os erros esperados num aviso) =================

    def clicar_guardar(self):
        executar_acao(self, self.guardar)

    def clicar_eliminar(self):
        executar_acao(self, self.eliminar)

    def clicar_atualizar(self):
        executar_acao(self, self.carregar)

    # ================= Ações =================

    def novo(self):
        self.id_selecionado = None
        for chave in self.campos:
            if chave == "custo_hora":
                self.campos[chave].set("0")
            else:
                self.campos[chave].set("")
        self.ativo.set(True)
        self.lista.selection_remove(self.lista.selection())
        self.estado.set("Novo técnico. Preencha os campos e clique em Guardar.")

    def carregar(self):
        tecnicos = self.controller.listar(self.apenas_ativos.get())
        self.lista.delete(*self.lista.get_children())
        for tecnico in tecnicos:
            if tecnico.ativo:
                ativo = "Sim"
            else:
                ativo = "Não"
            if tecnico.especialidade is None:
                especialidade = ""
            else:
                especialidade = tecnico.especialidade
            self.lista.insert("", "end", iid=str(tecnico.id_tecnico), values=(
                tecnico.id_tecnico, tecnico.nome, especialidade,
                round(tecnico.custo_hora, 2), ativo))
        self.novo()
        self.estado.set(str(len(tecnicos))
                        + " técnico(s). Selecione uma linha para editar.")

    def ao_selecionar(self, evento):
        if self.lista.selection():
            executar_acao(self, self.preencher_selecao)

    def preencher_selecao(self):
        tecnico = self.controller.obter(int(self.lista.selection()[0]))
        self.id_selecionado = tecnico.id_tecnico
        self.campos["nome"].set(tecnico.nome)
        if tecnico.especialidade is None:
            self.campos["especialidade"].set("")
        else:
            self.campos["especialidade"].set(tecnico.especialidade)
        self.campos["custo_hora"].set(str(tecnico.custo_hora))
        self.ativo.set(tecnico.ativo)
        self.estado.set("A editar o técnico " + str(tecnico.id_tecnico) + ".")

    def guardar(self):
        dados = {}
        for chave in self.campos:
            dados[chave] = self.campos[chave].get()
        tecnico = self.controller.guardar(dados, self.ativo.get(), self.id_selecionado)
        self.carregar()
        self.estado.set("Técnico " + str(tecnico.id_tecnico) + " guardado.")

    def eliminar(self):
        if self.id_selecionado is None:
            raise ValueError("Selecione primeiro um técnico na lista.")
        if perguntar_sim_nao(self, "Confirmar", "Eliminar o técnico selecionado?"):
            self.controller.eliminar(self.id_selecionado)
            self.carregar()
            self.estado.set("Técnico eliminado.")
