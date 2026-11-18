import tkinter as tk
from tkinter import ttk

from src.views.tema import configurar_linhas_alternadas, tags_linha_alternada
from src.views.estilo import (
    executar_acao, perguntar_sim_nao, PesquisaTabela, marcar_erro, preparar_campo
)
from src.services.validacao import validar_campos


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
        self.entradas = {}   # chave -> campo de texto, para pintar os que têm erro
        for chave, rotulo in rotulos:
            ttk.Label(self, text=rotulo).grid(row=linha, column=0, sticky="w", pady=2)
            entrada = tk.Entry(self, textvariable=self.campos[chave])
            entrada.grid(row=linha, column=1, sticky="ew", padx=8)
            preparar_campo(entrada)
            self.entradas[chave] = entrada
            if chave == "stock_atual":
                self.entrada_stock = entrada
            linha += 1

    def criar_botoes(self):
        botoes = ttk.Frame(self)
        botoes.grid(row=7, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Button(botoes, text="Nova", command=self.nova).pack(side="left")
        ttk.Button(botoes, text="Guardar",
                   command=self.clicar_guardar).pack(side="left", padx=6)
        ttk.Button(botoes, text="Eliminar", style="Perigo.TButton",
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
        # Barra de pesquisa por cima da lista, dentro do mesmo quadro: assim não
        # mexe nas linhas do formulário que ficam acima (a lista passa para a linha 1)
        quadro.rowconfigure(1, weight=1)
        self.pesquisa = PesquisaTabela(quadro, self.mostrar_contagem)
        self.pesquisa.quadro.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        colunas = [("id", "ID"), ("referencia", "Referência"), ("nome", "Nome"),
                   ("stock", "Stock"), ("minimo", "Mínimo"), ("compra", "Compra"),
                   ("venda", "Venda"), ("alerta", "Alerta")]
        nomes = []
        for coluna in colunas:
            nomes.append(coluna[0])

        self.lista = ttk.Treeview(quadro, columns=nomes, show="headings",
                                  selectmode="browse", height=7)
        configurar_linhas_alternadas(self.lista)
        for nome, titulo in colunas:
            self.lista.heading(nome, text=titulo)
            self.lista.column(nome, width=100, minwidth=50)
        self.lista.tag_configure("baixo", background="#fff2cc")
        self.lista.grid(row=1, column=0, sticky="nsew")
        self.pesquisa.associar(self.lista)

        barra = ttk.Scrollbar(quadro, orient="vertical", command=self.lista.yview)
        barra.grid(row=1, column=1, sticky="ns")
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
        linhas = []
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
                round(peca.preco_venda, 2), alerta),
                tags=tags_linha_alternada(self.lista, etiquetas))
            valores = (peca.id_peca, peca.referencia, peca.nome, peca.stock_atual,
                       peca.stock_minimo, round(peca.preco_compra, 2),
                       round(peca.preco_venda, 2), alerta)
            # As etiquetas (cor do stock baixo) vão junto, para a cor se manter
            # quando a linha volta a aparecer depois de limpar a pesquisa
            linhas.append((str(peca.id_peca), valores, etiquetas))
        self.pesquisa.definir_linhas(linhas)
        self.nova()
        self.mostrar_contagem(len(self.lista.get_children()), len(pecas))

    # Chamada pela PesquisaTabela sempre que a tabela é filtrada
    def mostrar_contagem(self, visiveis, total):
        if self.pesquisa.pesquisa_ativa():
            self.estado.set(str(visiveis) + " de " + str(total) + " peça(s).")
        else:
            self.estado.set(str(total) + " peça(s). Selecione uma linha para editar "
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
        dados = {chave: self.campos[chave].get().strip() for chave in self.campos}
        self.validar_formulario(dados)
        peca = self.controller.guardar(dados, self.id_selecionado)
        self.carregar()
        self.estado.set("Peça " + str(peca.id_peca) + " guardada.")

    # Valida os campos da peça. Se houver erros pinta esses campos a vermelho e
    # levanta ValueError com a lista toda: o executar_acao mostra-a num messagebox.
    # Porquê levantar o erro em vez de abrir aqui o messagebox: um messagebox dentro
    # deste método bloqueia os testes (esperam uma resposta que ninguém dá) e o
    # aviso fica igual aos outros erros da aplicação.
    def validar_formulario(self, dados):
        campos = {
            "Referência": ("referencia", dados["referencia"], None),
            "Nome": ("nome", dados["nome"], None),
            "Preço de compra": ("preco_compra", dados["preco_compra"], "decimal"),
            "Preço de venda": ("preco_venda", dados["preco_venda"], "decimal"),
            "Stock atual": ("stock_atual", dados["stock_atual"], "inteiro"),
            "Stock mínimo": ("stock_minimo", dados["stock_minimo"], "inteiro"),
        }
        a_validar = {}
        for rotulo in campos:
            chave, valor, tipo = campos[rotulo]
            a_validar[rotulo] = {"valor": valor, "tipo": tipo,
                                 "obrigatorio": chave in ("referencia", "nome")}
        erros = validar_campos(a_validar)

        # Os valores numéricos não podem ser negativos
        for rotulo in ("Preço de compra", "Preço de venda", "Stock atual", "Stock mínimo"):
            valor = campos[rotulo][1].replace(",", ".")
            try:
                if float(valor) < 0:
                    erros.append(rotulo + " não pode ser negativo.")
            except ValueError:
                pass   # já foi apanhado pelo validar_campos

        if len(erros) > 0:
            # Pinta os campos que falharam (o nome do campo aparece no início da mensagem)
            for rotulo in campos:
                for erro in erros:
                    if erro.startswith(rotulo + " "):
                        marcar_erro(self.entradas[campos[rotulo][0]])
            raise ValueError("\n".join(erros))

    def receber_stock(self):
        erros = validar_campos({
            "Quantidade": {"valor": self.movimento.get(), "tipo": "inteiro"},
            "Preço de compra": {"valor": self.campos["preco_compra"].get(), "tipo": "decimal"}})
        if len(erros) > 0:
            raise ValueError("\n".join(erros))
        peca = self.controller.receber_stock(
            self.exigir_selecao(), self.movimento.get(),
            self.campos["fornecedor"].get(), self.campos["preco_compra"].get())
        self.carregar()
        self.estado.set("Entrada registada. Stock da peça " + str(peca.id_peca)
                        + ": " + str(peca.stock_atual) + ".")

    def ajustar_stock(self):
        valor = self.movimento.get().strip()
        if not valor.lstrip("+-").isdigit() or valor in ("", "+", "-"):
            raise ValueError("A quantidade deve ser um número inteiro (pode ser negativo).")
        peca = self.controller.ajustar_stock(self.exigir_selecao(), valor)
        self.carregar()
        self.estado.set("Stock da peça " + str(peca.id_peca) + " ajustado para "
                        + str(peca.stock_atual) + ".")

    def eliminar(self):
        id_peca = self.exigir_selecao()
        if perguntar_sim_nao(self, "Confirmar", "Eliminar a peça selecionada?"):
            self.controller.eliminar(id_peca)
            self.carregar()
            self.estado.set("Peça eliminada.")
