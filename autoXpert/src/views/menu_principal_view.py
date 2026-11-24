import tkinter as tk
from tkinter import ttk, messagebox

from src.views.estilo import criar_cabecalho, perguntar_sim_nao, ajustar_janela


# Quantos botões de módulos por linha. Em duas colunas o menu fica baixo o suficiente
# para caber em ecrãs pequenos (1366x768) mesmo com todos os módulos de administrador.
COLUNAS_MENU = 2


class MenuPrincipalView:
    # Janela inicial do AutoXpert: um botão por módulo.
    # entradas é uma lista de (texto, função). Se a função for None, o módulo ainda
    # não existe e o botão aparece desativado ("em breve").

    # Inicializa o menu e recebe a função que consulta as estatísticas.
    def __init__(self, raiz, entradas, obter_sumario):
        self.raiz = raiz
        self.entradas = entradas
        self.obter_sumario = obter_sumario

        self.raiz.title("AutoXpert")
        self.raiz.geometry("560x600")
        self.raiz.resizable(False, False)

        criar_cabecalho(self.raiz, "AutoXpert")
        ttk.Label(self.raiz, text="Gestão de oficina").pack(pady=(10, 5))

        quadro = ttk.Frame(self.raiz, padding=(30, 5))
        quadro.pack(fill="both", expand=True)

        # Cria o painel que apresenta as estatísticas da oficina.
        painel = ttk.LabelFrame(quadro, text="Resumo", padding=10)
        painel.pack(fill="x", pady=(5, 10))

        # Cria variáveis para atualizar os valores apresentados.
        self.clientes_var = tk.StringVar(value="0")
        self.ordens_var = tk.StringVar(value="0")
        self.faturas_var = tk.StringVar(value="0")

        # Apresenta o número total de clientes.
        ttk.Label(painel, text="N.º de clientes:").grid(
            row=0, column=0, sticky="w", padx=5, pady=3
        )
        ttk.Label(painel, textvariable=self.clientes_var).grid(
            row=0, column=1, sticky="e", padx=5, pady=3
        )

        # Apresenta o número de ordens de trabalho abertas.
        ttk.Label(painel, text="Ordens abertas:").grid(
            row=1, column=0, sticky="w", padx=5, pady=3
        )
        ttk.Label(painel, textvariable=self.ordens_var).grid(
            row=1, column=1, sticky="e", padx=5, pady=3
        )

        # Apresenta o número de faturas pendentes.
        ttk.Label(painel, text="Faturas pendentes:").grid(
            row=2, column=0, sticky="w", padx=5, pady=3
        )
        ttk.Label(painel, textvariable=self.faturas_var).grid(
            row=2, column=1, sticky="e", padx=5, pady=3
        )

        # Permite atualizar as estatísticas manualmente.
        ttk.Button(
            painel,
            text="Atualizar",
            command=self.atualizar_sumario
        ).grid(row=3, column=0, columnspan=2, pady=(8, 2))

        # Alinha os valores à direita.
        painel.columnconfigure(1, weight=1)

        # Carrega as estatísticas quando o menu é aberto.
        self.atualizar_sumario()

        # "Sair" é criado antes dos módulos e fica fixo no fundo (side="bottom"):
        # assim nunca desaparece, mesmo num ecrã baixo.
        ttk.Button(quadro, text="Sair", command=self.sair).pack(side="bottom", pady=(8, 5))

        botoes = ttk.Frame(quadro)
        botoes.pack(fill="x")
        for coluna in range(COLUNAS_MENU):
            botoes.columnconfigure(coluna, weight=1, uniform="menu")
        for posicao, (texto_botao, comando) in enumerate(self.entradas):
            if comando is None:
                botao = ttk.Button(botoes, text=texto_botao + "  (em breve)",
                                   style="Menu.TButton", state="disabled")
            else:
                botao = ttk.Button(botoes, text=texto_botao, style="Menu.TButton",
                                   command=comando)
            botao.grid(row=posicao // COLUNAS_MENU, column=posicao % COLUNAS_MENU,
                       sticky="ew", padx=4, pady=3)

        self.raiz.protocol("WM_DELETE_WINDOW", self.sair)

        # A altura vem do conteúdo (resumo + um botão por módulo + Sair), por isso o
        # botão "Sair" nunca fica cortado, qualquer que seja o número de módulos.
        ajustar_janela(self.raiz, 560, 0)

    def atualizar_sumario(self):
        sumario = self.obter_sumario()

        self.clientes_var.set(
            str(sumario.get("clientes", "N/A"))
        )
        self.ordens_var.set(
            str(sumario.get("ordens_abertas", 0))
        )
        self.faturas_var.set(
            str(sumario.get("faturas_pendentes", "N/A"))
        )

    def sair(self):
        if messagebox.askyesno(
            "Sair",
            "Tem a certeza de que pretende sair da aplicação?"
        ):
            self.raiz.destroy()