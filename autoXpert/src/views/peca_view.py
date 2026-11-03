import tkinter as tk
from tkinter import ttk

from src.views.estilo import executar_acao, perguntar_sim_nao


class PecaView(ttk.Frame):
    # Página de gestão de peças e stock: formulário em cima, lista em baixo.
    # Só desenha e recolhe dados; o resto é pedido ao PecaController.

    def __init__(self, parent, controller):
        super().__init__(parent, padding=12)
        self.controller = controller
        self.id_selecionado = None  # peça que está a ser editada (None = nova)

        self.campos = {}
        valores_iniciais = [("referencia", ""), ("nome", ""), ("preco_compra", "0"),
                            ("preco_venda", "0"), ("stock_atual", "0"),
                            ("stock_minimo", "0"), ("fornecedor", "")]
        for chave, valor in valores_iniciais:
            self.campos[chave] = tk.StringVar(self, value=valor)

        self.apenas_stock_baixo = tk.BooleanVar(self, value=False)
        self.movimento = tk.StringVar(self, value="1")
        self.estado = tk.StringVar(self)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(10, weight=1)

        self.criar_formulario()
        self.criar_botoes()
        self.criar_movimentos()
        self.criar_lista()
        ttk.Label(self, textvariable=self.estado).grid(
            row=11, column=0, columnspan=2, sticky="w", pady=8)

        self.carregar()

    # ================= Construção da janela =================

    def criar_formulario(self):
        rotulos = [("referencia", "Referência *"), ("nome", "Nome *"),
                   ("preco_compra", "Preço de compra (€) *"),
                   ("preco_venda", "Preço de venda (€) *"),
                   ("stock_atual", "Stock inicial / atual *"),
                   ("stock_minimo", "Stock mínimo *"), ("fornecedor", "Fornecedor")]
        linha = 0
        for chave, rotulo in rotulos:
            ttk.Label(self, text=rotulo).grid(row=linha, column=0, sticky="w", pady=2)
            entrada = ttk.Entry(self, textvariable=self.campos[chave])
            entrada.grid(row=linha, column=1, sticky="ew", padx=8)
            if chave == "stock_atual":
                self.entrada_stock = entrada
            linha += 1

    def criar_botoes(self):
        botoes = ttk.Frame(self)
        botoes.grid(row=7, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Button(botoes, text="Nova", command=self.nova).pack(side="left")
        ttk.Button(botoes, text="Guardar",
                   command=self.clicar_guardar).pack(side="left", padx=6)
        ttk.Button(botoes, text="Eliminar",
                   command=self.clicar_eliminar).pack(side="left")
        ttk.Button(botoes, text="Atualizar lista",
                   command=self.clicar_atualizar).pack(side="left", padx=6)
        ttk.Checkbutton(botoes, text="Apenas stock baixo",
                        variable=self.apenas_stock_baixo,
                        command=self.clicar_atualizar).pack(side="left")

    def criar_movimentos(self):
        quadro = ttk.LabelFrame(self, text="Movimento da peça selecionada", padding=6)
        quadro.grid(row=8, column=0, columnspan=2, sticky="ew")
        ttk.Label(quadro, text="Quantidade / variação:").pack(side="left")
        ttk.Entry(quadro, textvariable=self.movimento, width=8).pack(side="left", padx=6)
        ttk.Button(quadro, text="Receber stock",
                   command=self.clicar_receber).pack(side="left", padx=6)
        ttk.Button(quadro, text="Ajustar (+/-)",
                   command=self.clicar_ajustar).pack(side="left")
        ttk.Label(
            self, text="Receber usa o fornecedor e o preço de compra do formulário. "
            "Ajustar aceita valores negativos para saídas."
        ).grid(row=9, column=0, columnspan=2, sticky="w", pady=6)

    def criar_lista(self):
        quadro = ttk.Frame(self)
        quadro.grid(row=10, column=0, columnspan=2, sticky="nsew")
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)

        colunas = [("id", "ID"), ("referencia", "Referência"), ("nome", "Nome"),
                   ("stock", "Stock"), ("minimo", "Mínimo"), ("compra", "Compra"),
                   ("venda", "Venda"), ("alerta", "Alerta")]
        nomes = []
        for coluna in colunas:
            nomes.append(coluna[0])

        self.lista = ttk.Treeview(quadro, columns=nomes, show="headings",
                                  selectmode="browse", height=7)
        for nome, titulo in colunas:
            self.lista.heading(nome, text=titulo)
            self.lista.column(nome, width=100, minwidth=50)
        self.lista.tag_configure("baixo", background="#fff2cc")
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

    def clicar_receber(self):
        executar_acao(self, self.receber_stock)

    def clicar_ajustar(self):
        executar_acao(self, self.ajustar_stock)

    # ================= Ações =================

    def nova(self):
        self.id_selecionado = None
        for chave in self.campos:
            if chave in ("referencia", "nome", "fornecedor"):
                self.campos[chave].set("")
            else:
                self.campos[chave].set("0")
        self.movimento.set("1")
        self.entrada_stock.configure(state="normal")
        self.lista.selection_remove(self.lista.selection())
        self.estado.set("Nova peça. O stock inicial só pode ser indicado na criação.")

    def carregar(self):
        pecas = self.controller.listar(self.apenas_stock_baixo.get())
        self.lista.delete(*self.lista.get_children())
        for peca in pecas:
            if peca.stock_baixo():
                alerta = "Stock baixo"
                etiquetas = ("baixo",)
            else:
                alerta = ""
                etiquetas = ()
            self.lista.insert("", "end", iid=str(peca.id_peca), values=(
                peca.id_peca, peca.referencia, peca.nome, peca.stock_atual,
                peca.stock_minimo, round(peca.preco_compra, 2),
                round(peca.preco_venda, 2), alerta), tags=etiquetas)
        self.nova()
        self.estado.set(str(len(pecas)) + " peça(s). Selecione uma linha para editar "
                        "ou movimentar stock.")

    def ao_selecionar(self, evento):
        if self.lista.selection():
            executar_acao(self, self.preencher_selecao)

    def preencher_selecao(self):
        peca = self.controller.obter(int(self.lista.selection()[0]))
        self.id_selecionado = peca.id_peca
        for chave in self.campos:
            valor = getattr(peca, chave)
            if valor is None:
                valor = ""
            self.campos[chave].set(str(valor))
        self.entrada_stock.configure(state="readonly")
        self.estado.set("A editar a peça " + str(peca.id_peca)
                        + ". Use os botões de movimento para alterar o stock.")

    def exigir_selecao(self):
        if self.id_selecionado is None:
            raise ValueError("Selecione primeiro uma peça na lista.")
        return self.id_selecionado

    def guardar(self):
        dados = {}
        for chave in self.campos:
            dados[chave] = self.campos[chave].get()
        peca = self.controller.guardar(dados, self.id_selecionado)
        self.carregar()
        self.estado.set("Peça " + str(peca.id_peca) + " guardada.")

    def receber_stock(self):
        peca = self.controller.receber_stock(
            self.exigir_selecao(), self.movimento.get(),
            self.campos["fornecedor"].get(), self.campos["preco_compra"].get())
        self.carregar()
        self.estado.set("Entrada registada. Stock da peça " + str(peca.id_peca)
                        + ": " + str(peca.stock_atual) + ".")

    def ajustar_stock(self):
        peca = self.controller.ajustar_stock(self.exigir_selecao(), self.movimento.get())
        self.carregar()
        self.estado.set("Stock da peça " + str(peca.id_peca) + " ajustado para "
                        + str(peca.stock_atual) + ".")

    def eliminar(self):
        id_peca = self.exigir_selecao()
        if perguntar_sim_nao(self, "Confirmar", "Eliminar a peça selecionada?"):
            self.controller.eliminar(id_peca)
            self.carregar()
            self.estado.set("Peça eliminada.")
