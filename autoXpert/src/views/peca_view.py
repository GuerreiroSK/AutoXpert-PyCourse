import tkinter as tk
from tkinter import messagebox, ttk

from src.controllers.peca_controller import PecaController
from src.views.mensagens import executar_acao


class PecaView(ttk.Frame):
    def __init__(self, parent: tk.Misc, controller: PecaController):
        super().__init__(parent, padding=12)
        self.controller = controller
        self.id_selecionado: int | None = None
        self.campos = {
            chave: tk.StringVar(self, value=valor)
            for chave, valor in (
                ("referencia", ""), ("nome", ""), ("preco_compra", "0"),
                ("preco_venda", "0"), ("stock_atual", "0"),
                ("stock_minimo", "0"), ("fornecedor", ""),
            )
        }
        self.apenas_stock_baixo = tk.BooleanVar(self, value=False)
        self.movimento = tk.StringVar(self, value="1")
        self.estado = tk.StringVar(self)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(10, weight=1)

        for linha, (chave, rotulo) in enumerate((
            ("referencia", "Referencia *"), ("nome", "Nome *"),
            ("preco_compra", "Preco de compra (EUR) *"),
            ("preco_venda", "Preco de venda (EUR) *"),
            ("stock_atual", "Stock inicial / atual *"),
            ("stock_minimo", "Stock minimo *"), ("fornecedor", "Fornecedor"),
        )):
            ttk.Label(self, text=rotulo).grid(row=linha, column=0, sticky="w", pady=2)
            entrada = ttk.Entry(self, textvariable=self.campos[chave])
            entrada.grid(row=linha, column=1, sticky="ew", padx=8)
            if chave == "stock_atual":
                self.entrada_stock = entrada

        botoes = ttk.Frame(self)
        botoes.grid(row=7, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Button(botoes, text="Nova", command=self.nova).pack(side="left")
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
            botoes, text="Apenas stock baixo", variable=self.apenas_stock_baixo,
            command=lambda: executar_acao(self, self.carregar),
        ).pack(side="left")

        stock = ttk.LabelFrame(self, text="Movimento da peca selecionada", padding=6)
        stock.grid(row=8, column=0, columnspan=2, sticky="ew")
        ttk.Label(stock, text="Quantidade / variacao:").pack(side="left")
        ttk.Entry(stock, textvariable=self.movimento, width=8).pack(side="left", padx=6)
        ttk.Button(
            stock, text="Receber stock",
            command=lambda: executar_acao(self, self.receber_stock),
        ).pack(side="left", padx=6)
        ttk.Button(
            stock, text="Ajustar (+/-)",
            command=lambda: executar_acao(self, self.ajustar_stock),
        ).pack(side="left")
        ttk.Label(
            self, text="Receber usa o fornecedor e preco de compra do formulario. "
            "Ajustar aceita valores negativos para saidas.",
        ).grid(row=9, column=0, columnspan=2, sticky="w", pady=6)

        tabela = ttk.Frame(self)
        tabela.grid(row=10, column=0, columnspan=2, sticky="nsew")
        tabela.columnconfigure(0, weight=1)
        tabela.rowconfigure(0, weight=1)
        colunas = ("id", "referencia", "nome", "stock", "minimo", "compra", "venda", "alerta")
        self.lista = ttk.Treeview(
            tabela, columns=colunas, show="headings", selectmode="browse", height=7
        )
        for coluna, rotulo in zip(
            colunas, ("ID", "Referencia", "Nome", "Stock", "Minimo", "Compra", "Venda", "Alerta")
        ):
            self.lista.heading(coluna, text=rotulo)
            self.lista.column(coluna, width=100, minwidth=50)
        self.lista.tag_configure("baixo", background="#fff2cc")
        self.lista.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(tabela, orient="vertical", command=self.lista.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.lista.configure(yscrollcommand=scroll.set)
        self.lista.bind("<<TreeviewSelect>>", self.ao_selecionar)
        ttk.Label(self, textvariable=self.estado).grid(
            row=11, column=0, columnspan=2, sticky="w", pady=8
        )
        self.carregar()

    def nova(self) -> None:
        self.id_selecionado = None
        for chave, variavel in self.campos.items():
            variavel.set("" if chave in ("referencia", "nome", "fornecedor") else "0")
        self.movimento.set("1")
        self.entrada_stock.configure(state="normal")
        self.lista.selection_remove(self.lista.selection())
        self.estado.set("Nova peca. O stock inicial so pode ser indicado na criacao.")

    def carregar(self) -> None:
        pecas = self.controller.listar(self.apenas_stock_baixo.get())
        self.lista.delete(*self.lista.get_children())
        for peca in pecas:
            self.lista.insert("", "end", iid=str(peca.id_peca), values=(
                peca.id_peca, peca.referencia, peca.nome,
                peca.stock_atual, peca.stock_minimo,
                f"{peca.preco_compra:.2f}", f"{peca.preco_venda:.2f}",
                "Stock baixo" if peca.stock_baixo else "",
            ), tags=("baixo",) if peca.stock_baixo else ())
        self.nova()
        self.estado.set(f"{len(pecas)} peca(s). Selecione uma linha para editar ou movimentar stock.")

    def ao_selecionar(self, evento: tk.Event) -> None:
        if self.lista.selection():
            executar_acao(self, self.preencher_selecao)

    def preencher_selecao(self) -> None:
        peca = self.controller.obter(int(self.lista.selection()[0]))
        self.id_selecionado = peca.id_peca
        for chave, variavel in self.campos.items():
            valor = getattr(peca, chave)
            variavel.set("" if valor is None else str(valor))
        self.entrada_stock.configure(state="readonly")
        self.estado.set(f"A editar a peca {peca.id_peca}. Use os botoes de movimento para alterar stock.")

    def exigir_selecao(self) -> int:
        if self.id_selecionado is None:
            raise ValueError("Selecione primeiro uma peca na lista.")
        return self.id_selecionado

    def guardar(self) -> None:
        dados = {chave: variavel.get() for chave, variavel in self.campos.items()}
        peca = self.controller.guardar(dados, self.id_selecionado)
        self.carregar()
        self.estado.set(f"Peca {peca.id_peca} guardada.")

    def receber_stock(self) -> None:
        peca = self.controller.receber_stock(
            self.exigir_selecao(), self.movimento.get(),
            self.campos["fornecedor"].get(), self.campos["preco_compra"].get(),
        )
        self.carregar()
        self.estado.set(f"Entrada registada. Stock da peca {peca.id_peca}: {peca.stock_atual}.")

    def ajustar_stock(self) -> None:
        peca = self.controller.ajustar_stock(self.exigir_selecao(), self.movimento.get())
        self.carregar()
        self.estado.set(f"Stock da peca {peca.id_peca} ajustado para {peca.stock_atual}.")

    def eliminar(self) -> None:
        id_peca = self.exigir_selecao()
        if messagebox.askyesno("Confirmar", "Eliminar a peca selecionada?", parent=self):
            self.controller.eliminar(id_peca)
            self.carregar()
            self.estado.set("Peca eliminada.")
