import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from src.views.linha_ot_view import PainelLinhasOT


class JanelaOTs:
    # Janela principal das Ordens de Trabalho.
    # A view só desenha e recolhe o que o utilizador escreve: não tem SQL nem regras.
    # Tudo o que é lógica é pedido ao controller, que devolve (ok, resultado).
    # As linhas da OT têm o seu próprio painel (PainelLinhasOT, em linha_ot_view.py).

    def __init__(self, raiz, controller, controller_linhas):
        self.raiz = raiz
        self.controller = controller
        self.controller_linhas = controller_linhas
        self.estados = self.controller.lista_estados()
        self.id_ot_atual = None  # OT que está selecionada na lista

        self.raiz.title("AutoXpert - Ordens de Trabalho")
        self.raiz.geometry("1180x760")

        self.criar_pesquisa()
        self.criar_lista()
        self.criar_detalhe()
        self.criar_barra_de_mensagens()

        self.mostrar_lista(self.controller.listar_todas())

    # ================= Construção da janela =================

    def criar_pesquisa(self):
        quadro = ttk.LabelFrame(self.raiz, text="Pesquisa")
        quadro.pack(fill="x", padx=10, pady=(10, 5))
        quadro.columnconfigure(8, weight=1)  # a coluna 8 absorve o espaço livre à direita

        # Linha 0: histórico por matrícula (RF07), atalhos (RF14) e nova OT
        ttk.Label(quadro, text="Matrícula:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entrada_matricula = ttk.Entry(quadro, width=12)
        self.entrada_matricula.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_matricula.bind("<Return>", self.ao_enter_matricula)
        ttk.Button(quadro, text="Histórico da viatura",
                   command=self.pesquisar_historico).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(quadro, text="Em curso",
                   command=self.mostrar_em_curso).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(quadro, text="Todas",
                   command=self.mostrar_todas).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(quadro, text="Nova OT",
                   command=self.abrir_nova_ot).grid(row=0, column=8, padx=5, pady=5, sticky="e")

        # Linha 1: filtros por estado, técnico e datas (RF12)
        ttk.Label(quadro, text="Estado:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_filtro_estado = ttk.Combobox(quadro, values=[""] + self.estados,
                                                state="readonly", width=14)
        self.combo_filtro_estado.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(quadro, text="Técnico (id):").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entrada_filtro_tecnico = ttk.Entry(quadro, width=6)
        self.entrada_filtro_tecnico.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(quadro, text="De:").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.entrada_data_de = ttk.Entry(quadro, width=11)
        self.entrada_data_de.grid(row=1, column=5, padx=5, pady=5)

        ttk.Label(quadro, text="Até:").grid(row=1, column=6, padx=5, pady=5, sticky="e")
        self.entrada_data_ate = ttk.Entry(quadro, width=11)
        self.entrada_data_ate.grid(row=1, column=7, padx=5, pady=5)

        ttk.Button(quadro, text="Filtrar",
                   command=self.pesquisar_filtros).grid(row=1, column=8, padx=5, pady=5, sticky="e")

        ttk.Label(quadro, text="Datas no formato AAAA-MM-DD").grid(
            row=2, column=0, columnspan=6, padx=5, pady=(0, 5), sticky="w")

    def criar_lista(self):
        quadro = ttk.Frame(self.raiz)
        quadro.pack(fill="x", padx=10, pady=5)

        colunas = [("id", "OT", 50), ("viatura", "Viatura", 70), ("tecnico", "Técnico", 70),
                   ("entrada", "Entrada", 110), ("prev", "Prev. saída", 110),
                   ("saida", "Saída real", 110), ("estado", "Estado", 120),
                   ("custo", "Custo (€)", 90)]
        nomes = []
        for coluna in colunas:
            nomes.append(coluna[0])

        self.lista = ttk.Treeview(quadro, columns=nomes, show="headings",
                                  height=7, selectmode="browse")
        for nome, titulo, largura in colunas:
            self.lista.heading(nome, text=titulo)
            self.lista.column(nome, width=largura, anchor="center")

        barra = ttk.Scrollbar(quadro, orient="vertical", command=self.lista.yview)
        self.lista.configure(yscrollcommand=barra.set)
        self.lista.pack(side="left", fill="x", expand=True)
        barra.pack(side="right", fill="y")

        self.lista.bind("<<TreeviewSelect>>", self.ao_selecionar_ot)

    def criar_detalhe(self):
        quadro = ttk.LabelFrame(self.raiz, text="OT selecionada")
        quadro.pack(fill="both", expand=True, padx=10, pady=5)

        self.label_resumo = ttk.Label(quadro, text="Nenhuma OT selecionada",
                                      wraplength=1100, justify="left")
        self.label_resumo.pack(fill="x", padx=10, pady=(8, 4))

        # Estado (RF06) e técnico (RF05)
        acoes = ttk.Frame(quadro)
        acoes.pack(fill="x", padx=10, pady=4)

        ttk.Label(acoes, text="Estado:").grid(row=0, column=0, padx=5, sticky="e")
        self.combo_estado = ttk.Combobox(acoes, values=self.estados, state="readonly", width=14)
        self.combo_estado.grid(row=0, column=1, padx=5)

        ttk.Label(acoes, text="Data de saída (ao entregar):").grid(
            row=0, column=2, padx=(15, 5), sticky="e")
        self.entrada_data_saida = ttk.Entry(acoes, width=11)
        self.entrada_data_saida.grid(row=0, column=3, padx=5)
        self.escrever(self.entrada_data_saida, date.today().isoformat())

        ttk.Button(acoes, text="Mudar estado",
                   command=self.mudar_estado).grid(row=0, column=4, padx=(10, 5))

        ttk.Label(acoes, text="Técnico (id):").grid(row=0, column=5, padx=(30, 5), sticky="e")
        self.entrada_tecnico = ttk.Entry(acoes, width=6)
        self.entrada_tecnico.grid(row=0, column=6, padx=5)
        ttk.Button(acoes, text="Atribuir técnico",
                   command=self.atribuir_tecnico).grid(row=0, column=7, padx=5)

        # Linhas da OT (RF04): painel próprio, definido em linha_ot_view.py
        self.painel_linhas = PainelLinhasOT(quadro, self.controller_linhas,
                                            self.ao_mudar_linhas)
        self.painel_linhas.quadro.pack(fill="both", expand=True, padx=10, pady=6)

        self.label_custo = ttk.Label(quadro, text="Custo total: -",
                                     font=("TkDefaultFont", 12, "bold"))
        self.label_custo.pack(anchor="e", padx=20, pady=(0, 10))

    def criar_barra_de_mensagens(self):
        self.mensagem = tk.StringVar()
        barra = ttk.Label(self.raiz, textvariable=self.mensagem, relief="sunken", anchor="w")
        barra.pack(fill="x", side="bottom")

    # ================= Funções auxiliares =================

    # Apaga o conteúdo de uma caixa de texto e escreve o novo
    def escrever(self, entrada, texto):
        entrada.delete(0, "end")
        entrada.insert(0, str(texto))

    # None aparece como texto vazio
    def texto(self, valor):
        if valor is None:
            return ""
        return valor

    def dizer(self, texto):
        self.mensagem.set(texto)

    def mostrar_erro(self, mensagem):
        messagebox.showerror("Erro", mensagem, parent=self.raiz)
        self.dizer("")

    def valores_da_ot(self, ot):
        return (ot.id_ot, ot.id_viatura, ot.id_tecnico, ot.data_entrada,
                ot.data_prev_saida, self.texto(ot.data_saida_real), ot.estado,
                round(ot.custo_total, 2))

    # Devolve o id da OT selecionada, ou avisa o utilizador se não houver nenhuma
    def ot_selecionada(self):
        if self.id_ot_atual is None:
            messagebox.showinfo("Atenção", "Selecione primeiro uma OT na lista.",
                                parent=self.raiz)
            return None
        return self.id_ot_atual

    # ================= Lista de OTs =================

    # Recebe o par (ok, resultado) que o controller devolve
    def mostrar_lista(self, resultado):
        ok, dados = resultado
        if not ok:
            self.mostrar_erro(dados)
            return
        for item in self.lista.get_children():
            self.lista.delete(item)
        for ot in dados:
            self.lista.insert("", "end", iid=str(ot.id_ot), values=self.valores_da_ot(ot))
        self.limpar_detalhe()
        self.dizer(str(len(dados)) + " OT(s) encontrada(s)")

    def mostrar_todas(self):
        self.mostrar_lista(self.controller.listar_todas())

    # RF14
    def mostrar_em_curso(self):
        self.mostrar_lista(self.controller.listar_em_curso())

    # RF07
    def pesquisar_historico(self):
        self.mostrar_lista(self.controller.historico_por_matricula(
            self.entrada_matricula.get()))

    def ao_enter_matricula(self, evento):
        self.pesquisar_historico()

    # RF12
    def pesquisar_filtros(self):
        self.mostrar_lista(self.controller.pesquisar(
            self.entrada_data_de.get(), self.entrada_data_ate.get(),
            self.combo_filtro_estado.get(), self.entrada_filtro_tecnico.get()))

    def ao_selecionar_ot(self, evento):
        selecionadas = self.lista.selection()
        if len(selecionadas) == 0:
            return
        self.carregar_detalhe(int(selecionadas[0]))

    # ================= Detalhe da OT =================

    def limpar_detalhe(self):
        self.id_ot_atual = None
        self.label_resumo.config(text="Nenhuma OT selecionada")
        self.combo_estado.set("")
        self.entrada_tecnico.delete(0, "end")
        self.label_custo.config(text="Custo total: -")
        self.painel_linhas.limpar()

    # Mostra os dados da OT (resumo, estado, técnico, custo total) e atualiza a
    # linha da lista. Devolve True se correu bem.
    def atualizar_dados_da_ot(self, id_ot):
        ok, ot = self.controller.obter_ot(id_ot)
        if not ok:
            self.mostrar_erro(ot)
            return False
        self.id_ot_atual = id_ot

        self.label_resumo.config(
            text=("OT " + str(ot.id_ot) + "   |   Viatura " + str(ot.id_viatura)
                  + "   |   Técnico " + str(ot.id_tecnico)
                  + "   |   Entrada: " + str(ot.data_entrada)
                  + "   |   Prevista: " + str(ot.data_prev_saida)
                  + "\nAvaria: " + str(ot.descricao_avaria)))
        self.combo_estado.set(ot.estado)
        self.escrever(self.entrada_tecnico, ot.id_tecnico)
        self.label_custo.config(text="Custo total: " + str(round(ot.custo_total, 2)) + " €")

        if self.lista.exists(str(id_ot)):
            self.lista.item(str(id_ot), values=self.valores_da_ot(ot))
        return True

    # Mostra a OT e também as suas linhas
    def carregar_detalhe(self, id_ot):
        if self.atualizar_dados_da_ot(id_ot):
            self.painel_linhas.mostrar_linhas(id_ot)

    # Chamado pelo painel das linhas quando uma linha foi adicionada ou removida:
    # o custo total da OT mudou, por isso atualiza-se o detalhe e a lista
    def ao_mudar_linhas(self, id_ot, mensagem):
        self.atualizar_dados_da_ot(id_ot)
        self.dizer(mensagem)

    # ================= Ações sobre a OT =================

    # RF06
    def mudar_estado(self):
        id_ot = self.ot_selecionada()
        if id_ot is None:
            return
        ok, resultado = self.controller.mudar_estado(
            id_ot, self.combo_estado.get(), self.entrada_data_saida.get())
        if not ok:
            self.mostrar_erro(resultado)
            self.carregar_detalhe(id_ot)  # volta a mostrar o estado verdadeiro
            return
        self.carregar_detalhe(id_ot)
        self.dizer("Estado da OT " + str(id_ot) + " alterado para " + resultado.estado)

    # RF05
    def atribuir_tecnico(self):
        id_ot = self.ot_selecionada()
        if id_ot is None:
            return
        ok, resultado = self.controller.atribuir_tecnico(id_ot, self.entrada_tecnico.get())
        if not ok:
            self.mostrar_erro(resultado)
            self.carregar_detalhe(id_ot)
            return
        self.carregar_detalhe(id_ot)
        self.dizer("Técnico da OT " + str(id_ot) + " alterado para " + str(resultado.id_tecnico))

    # ================= Nova OT =================

    def abrir_nova_ot(self):
        DialogoNovaOT(self.raiz, self.controller, self.ao_criar_ot)

    # Chamado pelo diálogo quando a OT foi criada
    def ao_criar_ot(self, ot):
        self.mostrar_todas()
        self.lista.selection_set(str(ot.id_ot))
        self.lista.see(str(ot.id_ot))
        self.carregar_detalhe(ot.id_ot)
        self.dizer("OT " + str(ot.id_ot) + " criada com sucesso")


class DialogoNovaOT:
    # Pequena janela para criar uma OT (RF03 + RF05). O técnico é obrigatório.

    def __init__(self, janela_pai, controller, ao_criar):
        self.controller = controller
        self.ao_criar = ao_criar  # função da janela principal, chamada com a OT criada

        self.janela = tk.Toplevel(janela_pai)
        self.janela.title("Nova Ordem de Trabalho")
        self.janela.transient(janela_pai)
        self.janela.wait_visibility()  # no Linux, o grab só funciona com a janela já visível
        self.janela.grab_set()  # enquanto está aberta, só se mexe nesta janela

        hoje = date.today().isoformat()

        ttk.Label(self.janela, text="ID da viatura:").grid(row=0, column=0, padx=10, pady=6, sticky="e")
        self.entrada_viatura = ttk.Entry(self.janela, width=10)
        self.entrada_viatura.grid(row=0, column=1, padx=10, pady=6, sticky="w")

        ttk.Label(self.janela, text="ID do técnico:").grid(row=1, column=0, padx=10, pady=6, sticky="e")
        self.entrada_tecnico = ttk.Entry(self.janela, width=10)
        self.entrada_tecnico.grid(row=1, column=1, padx=10, pady=6, sticky="w")

        ttk.Label(self.janela, text="Data de entrada:").grid(row=2, column=0, padx=10, pady=6, sticky="e")
        self.entrada_data_entrada = ttk.Entry(self.janela, width=12)
        self.entrada_data_entrada.grid(row=2, column=1, padx=10, pady=6, sticky="w")
        self.entrada_data_entrada.insert(0, hoje)

        ttk.Label(self.janela, text="Data prevista de saída:").grid(row=3, column=0, padx=10, pady=6, sticky="e")
        self.entrada_data_prevista = ttk.Entry(self.janela, width=12)
        self.entrada_data_prevista.grid(row=3, column=1, padx=10, pady=6, sticky="w")
        self.entrada_data_prevista.insert(0, hoje)

        ttk.Label(self.janela, text="Descrição da avaria:").grid(row=4, column=0, padx=10, pady=6, sticky="e")
        self.entrada_descricao = ttk.Entry(self.janela, width=45)
        self.entrada_descricao.grid(row=4, column=1, padx=10, pady=6, sticky="w")

        ttk.Label(self.janela, text="Datas no formato AAAA-MM-DD").grid(
            row=5, column=1, padx=10, sticky="w")

        botoes = ttk.Frame(self.janela)
        botoes.grid(row=6, column=0, columnspan=2, pady=12)
        ttk.Button(botoes, text="Criar OT", command=self.criar).pack(side="left", padx=8)
        ttk.Button(botoes, text="Cancelar", command=self.janela.destroy).pack(side="left", padx=8)

        # Abre por cima da janela principal (em vez de no canto do ecrã)
        x = janela_pai.winfo_rootx() + 250
        y = janela_pai.winfo_rooty() + 150
        self.janela.geometry("+" + str(x) + "+" + str(y))

        self.entrada_viatura.focus_set()

    def criar(self):
        ok, resultado = self.controller.criar_ot(
            self.entrada_viatura.get(), self.entrada_tecnico.get(),
            self.entrada_data_entrada.get(), self.entrada_data_prevista.get(),
            self.entrada_descricao.get())
        if not ok:
            messagebox.showerror("Erro", resultado, parent=self.janela)
            return
        self.janela.destroy()
        self.ao_criar(resultado)
