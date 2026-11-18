import tkinter as tk
from tkinter import ttk, messagebox

from src.views.estilo import criar_cabecalho, perguntar_sim_nao


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
        # Reserva espaço adicional para o painel de sumário.
        self.raiz.geometry("440x" + str(300 + 62 * len(entradas)))
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

        for texto_botao, comando in self.entradas:
            if comando is None:
                botao = ttk.Button(quadro, text=texto_botao + "  (em breve)",
                                   style="Menu.TButton", state="disabled")
            else:
                botao = ttk.Button(quadro, text=texto_botao, style="Menu.TButton",
                                   command=comando)
            botao.pack(fill="x", pady=4)

        ttk.Button(quadro, text="Sair", command=self.sair).pack(pady=(12, 5))

        self.raiz.protocol("WM_DELETE_WINDOW", self.sair)

    # Consulta novamente os dados e atualiza os valores do painel.
    def atualizar_sumario(self):
        try:
            dados = self.obter_sumario()

            self.clientes_var.set(str(dados["clientes"]))
            self.ordens_var.set(str(dados["ordens_abertas"]))
            self.faturas_var.set(str(dados["faturas_pendentes"]))

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                "Não foi possível atualizar o sumário:\n" + str(erro),
                parent=self.raiz
            )

    def sair(self):
        if perguntar_sim_nao(self.raiz, "Sair", "Quer mesmo sair do AutoXpert?"):
            self.raiz.destroy()
