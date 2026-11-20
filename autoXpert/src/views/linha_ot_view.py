import tkinter as tk
from tkinter import ttk

from src.views.estilo import mostrar_erro, mostrar_info, perguntar_sim_nao
from src.views.tema import configurar_linhas_alternadas, tags_linha_alternada
from src.services.validacao import validar_campos

from src.views.estilo import (
    mostrar_erro, mostrar_info, perguntar_sim_nao, marcar_erro, preparar_campo
)


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
        # Ordem importa: formulário e botões são empacotados primeiro (side="bottom")
        # para ficarem sempre visíveis; a tabela, que pode encolher, vem a seguir.
        self.criar_formulario()
        self.criar_tabela()

    # ================= Construção do painel =================

    def criar_tabela(self):
        colunas = [("id", "Linha", 50), ("tipo", "Tipo", 80), ("descricao", "Descrição", 330),
                   ("qtd", "Qtd", 60), ("horas", "Horas", 60), ("preco", "Preço unit.", 90),
                   ("peca", "Peça", 60), ("subtotal", "Subtotal", 90)]
        nomes = []
        for coluna in colunas:
            nomes.append(coluna[0])

        self.tabela = ttk.Treeview(self.quadro, columns=nomes, show="headings",
                                   height=4, selectmode="browse")
        configurar_linhas_alternadas(self.tabela)
        for nome, titulo, largura in colunas:
            self.tabela.heading(nome, text=titulo)
            if nome == "descricao":
                self.tabela.column(nome, width=largura, anchor="w")
            else:
                self.tabela.column(nome, width=largura, anchor="center")
        self.tabela.pack(fill="both", expand=True, pady=(0, 6))

    def criar_formulario(self):
        # Os botões ficam no fundo do painel e o formulário logo acima deles
        botoes = ttk.Frame(self.quadro)
        botoes.pack(side="bottom", fill="x", pady=(4, 0))
        form = ttk.Frame(self.quadro)
        form.pack(side="bottom", fill="x", pady=4)

        ttk.Label(form, text="Tipo:").grid(row=0, column=0, padx=5, sticky="e")
        self.combo_tipo = ttk.Combobox(form, values=self.tipos, state="readonly", width=9)
        self.combo_tipo.grid(row=0, column=1, padx=5)
        self.combo_tipo.set(self.tipos[0])

        ttk.Label(form, text="Descrição:").grid(row=0, column=2, padx=(10, 5), sticky="e")
        self.entrada_descricao = tk.Entry(form, width=30)
        self.entrada_descricao.grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Qtd:").grid(row=0, column=4, padx=(10, 5), sticky="e")
        self.entrada_quantidade = tk.Entry(form, width=6)
        self.entrada_quantidade.grid(row=0, column=5, padx=5)

        ttk.Label(form, text="Preço unit.:").grid(row=0, column=6, padx=(10, 5), sticky="e")
        self.entrada_preco = tk.Entry(form, width=8)
        self.entrada_preco.grid(row=0, column=7, padx=5)

        ttk.Label(form, text="Horas:").grid(row=0, column=8, padx=(10, 5), sticky="e")
        self.entrada_horas = tk.Entry(form, width=6)
        self.entrada_horas.grid(row=0, column=9, padx=5)

        ttk.Label(form, text="Peça (id):").grid(row=0, column=10, padx=(10, 5), sticky="e")
        self.entrada_peca = tk.Entry(form, width=6)
        self.entrada_peca.grid(row=0, column=11, padx=5)
        # Os campos ficam a vermelho quando têm erro e voltam ao normal ao serem corrigidos
        for campo_texto in (self.entrada_descricao, self.entrada_quantidade,
                            self.entrada_preco, self.entrada_horas, self.entrada_peca):
            preparar_campo(campo_texto)

        ttk.Button(botoes, text="Adicionar linha",
                   command=self.adicionar_linha).pack(side="left", padx=5)
        ttk.Button(botoes, text="Remover linha selecionada",
                   style="Perigo.TButton",
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
        mostrar_erro(self.quadro, "Erro", mensagem)

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
                self.texto(linha.id_peca), linha.subtotal()),
                tags=tags_linha_alternada(self.tabela))

    # Esvazia a tabela (quando não há nenhuma OT selecionada)
    def limpar(self):
        self.id_ot_atual = None
        self.limpar_tabela()

    # ================= Ações =================

    # Diz se o texto é um número (aceita vírgula decimal)
    def e_numero(self, valor):
        try:
            float(valor.strip().replace(",", "."))
            return True
        except ValueError:
            return False

    # RF04 + RF13: o custo total é recalculado pelo service
    def adicionar_linha(self):
        if self.id_ot_atual is None:
            mostrar_info(self.quadro, "Atenção", "Selecione primeiro uma OT na lista.")
            return
        dados_validar = {
            "Descrição": self.entrada_descricao.get(),
            "Quantidade": {"valor": self.entrada_quantidade.get(), "tipo": "inteiro"},
            "Preço unitário": {"valor": self.entrada_preco.get(), "tipo": "decimal"},
        }
        erros = validar_campos(dados_validar)
        horas = self.entrada_horas.get().strip()
        if horas:
            try:
                if float(horas.replace(",", ".")) < 0:
                    erros.append("As horas não podem ser negativas.")
            except ValueError:
                erros.append("As horas devem ser um número válido.")
        peca = self.entrada_peca.get().strip()
        if peca and not peca.isdigit():
            erros.append("O ID da peça deve conter apenas números.")
        if erros:
            # Pinta a vermelho os campos obrigatórios vazios; os valores inválidos
            # (letras num número, etc.) ficam também a vermelho
            for entrada in (self.entrada_descricao, self.entrada_quantidade,
                            self.entrada_preco):
                if not entrada.get().strip():
                    marcar_erro(entrada)
            for entrada in (self.entrada_quantidade, self.entrada_preco):
                if entrada.get().strip() and not self.e_numero(entrada.get()):
                    marcar_erro(entrada)
            if horas and not self.e_numero(horas):
                marcar_erro(self.entrada_horas)
            if peca and not peca.isdigit():
                marcar_erro(self.entrada_peca)
            mostrar_erro(self.quadro, "Erro de validação", "\n".join(erros))
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
            mostrar_info(self.quadro, "Atenção", "Selecione primeiro uma OT na lista.")
            return
        selecionadas = self.tabela.selection()
        if len(selecionadas) == 0:
            mostrar_info(self.quadro, "Atenção", "Selecione primeiro uma linha na tabela.")
            return
        if not perguntar_sim_nao(self.quadro, "Remover linha",
                                 "Remover a linha selecionada?"):
            return
        id_ot = self.id_ot_atual
        ok, resultado = self.controller.remover_linha(int(selecionadas[0]))
        if not ok:
            self.mostrar_erro(resultado)
            return
        self.mostrar_linhas(id_ot)
        self.ao_alterar(id_ot, "Linha removida da OT " + str(id_ot))
