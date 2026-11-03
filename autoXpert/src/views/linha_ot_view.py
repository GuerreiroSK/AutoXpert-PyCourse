from tkinter import ttk, messagebox


class PainelLinhasOT:
    # Painel com a tabela das linhas de uma OT e o formulário para adicionar/remover linhas.
    # Não é uma janela: é um quadro (self.quadro) que a janela das OTs (ot_view.py)
    # coloca lá dentro. Tal como as outras views, só desenha e recolhe o que o
    # utilizador escreve; tudo o que é lógica é pedido ao LinhaOTController.
    #
    # ao_alterar é uma função da janela das OTs, chamada quando as linhas mudam
    # (para ela atualizar o custo total):  ao_alterar(id_ot, mensagem)

    def __init__(self, pai, controller, ao_alterar):
        self.controller = controller
        self.ao_alterar = ao_alterar
        self.tipos = self.controller.lista_tipos_linha()
        self.id_ot_atual = None  # OT cujas linhas estão a ser mostradas

        self.quadro = ttk.Frame(pai)
        self.criar_tabela()
        self.criar_formulario()

    # ================= Construção do painel =================

    def criar_tabela(self):
        colunas = [("id", "Linha", 50), ("tipo", "Tipo", 80), ("descricao", "Descrição", 330),
                   ("qtd", "Qtd", 60), ("horas", "Horas", 60), ("preco", "Preço unit.", 90),
                   ("peca", "Peça", 60), ("subtotal", "Subtotal", 90)]
        nomes = []
        for coluna in colunas:
            nomes.append(coluna[0])

        self.tabela = ttk.Treeview(self.quadro, columns=nomes, show="headings",
                                   height=5, selectmode="browse")
        for nome, titulo, largura in colunas:
            self.tabela.heading(nome, text=titulo)
            if nome == "descricao":
                self.tabela.column(nome, width=largura, anchor="w")
            else:
                self.tabela.column(nome, width=largura, anchor="center")
        self.tabela.pack(fill="both", expand=True, pady=(0, 6))

    def criar_formulario(self):
        form = ttk.Frame(self.quadro)
        form.pack(fill="x", pady=4)

        ttk.Label(form, text="Tipo:").grid(row=0, column=0, padx=5, sticky="e")
        self.combo_tipo = ttk.Combobox(form, values=self.tipos, state="readonly", width=9)
        self.combo_tipo.grid(row=0, column=1, padx=5)
        self.combo_tipo.set(self.tipos[0])

        ttk.Label(form, text="Descrição:").grid(row=0, column=2, padx=(10, 5), sticky="e")
        self.entrada_descricao = ttk.Entry(form, width=30)
        self.entrada_descricao.grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Qtd:").grid(row=0, column=4, padx=(10, 5), sticky="e")
        self.entrada_quantidade = ttk.Entry(form, width=6)
        self.entrada_quantidade.grid(row=0, column=5, padx=5)

        ttk.Label(form, text="Preço unit.:").grid(row=0, column=6, padx=(10, 5), sticky="e")
        self.entrada_preco = ttk.Entry(form, width=8)
        self.entrada_preco.grid(row=0, column=7, padx=5)

        ttk.Label(form, text="Horas:").grid(row=0, column=8, padx=(10, 5), sticky="e")
        self.entrada_horas = ttk.Entry(form, width=6)
        self.entrada_horas.grid(row=0, column=9, padx=5)

        ttk.Label(form, text="Peça (id):").grid(row=0, column=10, padx=(10, 5), sticky="e")
        self.entrada_peca = ttk.Entry(form, width=6)
        self.entrada_peca.grid(row=0, column=11, padx=5)

        botoes = ttk.Frame(self.quadro)
        botoes.pack(fill="x", pady=(4, 0))
        ttk.Button(botoes, text="Adicionar linha",
                   command=self.adicionar_linha).pack(side="left", padx=5)
        ttk.Button(botoes, text="Remover linha selecionada",
                   command=self.remover_linha).pack(side="left", padx=5)

    # ================= Funções auxiliares =================

    # None aparece como texto vazio
    def texto(self, valor):
        if valor is None:
            return ""
        return valor

    def limpar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

    def mostrar_erro(self, mensagem):
        messagebox.showerror("Erro", mensagem, parent=self.quadro)

    # ================= Usado pela janela das OTs =================

    # Mostra as linhas da OT indicada
    def mostrar_linhas(self, id_ot):
        ok, linhas = self.controller.listar_linhas(id_ot)
        if not ok:
            self.mostrar_erro(linhas)
            return
        self.id_ot_atual = id_ot
        self.limpar_tabela()
        for linha in linhas:
            self.tabela.insert("", "end", iid=str(linha.id_linha), values=(
                linha.id_linha, linha.tipo, linha.descricao, linha.quantidade,
                self.texto(linha.horas_trabalhadas), linha.preco_unitario,
                self.texto(linha.id_peca), linha.subtotal()))

    # Esvazia a tabela (quando não há nenhuma OT selecionada)
    def limpar(self):
        self.id_ot_atual = None
        self.limpar_tabela()

    # ================= Ações =================

    # RF04 + RF13: o custo total é recalculado pelo service
    def adicionar_linha(self):
        if self.id_ot_atual is None:
            messagebox.showinfo("Atenção", "Selecione primeiro uma OT na lista.",
                                parent=self.quadro)
            return
        id_ot = self.id_ot_atual
        ok, resultado = self.controller.adicionar_linha(
            id_ot, self.combo_tipo.get(), self.entrada_descricao.get(),
            self.entrada_quantidade.get(), self.entrada_preco.get(),
            self.entrada_horas.get(), self.entrada_peca.get())
        if not ok:
            self.mostrar_erro(resultado)
            return
        for entrada in [self.entrada_descricao, self.entrada_quantidade, self.entrada_preco,
                        self.entrada_horas, self.entrada_peca]:
            entrada.delete(0, "end")
        self.mostrar_linhas(id_ot)
        self.ao_alterar(id_ot, "Linha adicionada à OT " + str(id_ot))

    def remover_linha(self):
        if self.id_ot_atual is None:
            messagebox.showinfo("Atenção", "Selecione primeiro uma OT na lista.",
                                parent=self.quadro)
            return
        selecionadas = self.tabela.selection()
        if len(selecionadas) == 0:
            messagebox.showinfo("Atenção", "Selecione primeiro uma linha na tabela.",
                                parent=self.quadro)
            return
        if not messagebox.askyesno("Remover linha", "Remover a linha selecionada?",
                                   parent=self.quadro):
            return
        id_ot = self.id_ot_atual
        ok, resultado = self.controller.remover_linha(int(selecionadas[0]))
        if not ok:
            self.mostrar_erro(resultado)
            return
        self.mostrar_linhas(id_ot)
        self.ao_alterar(id_ot, "Linha removida da OT " + str(id_ot))
