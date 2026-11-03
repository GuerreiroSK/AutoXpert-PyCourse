import tkinter as tk
from tkinter import ttk

from src.views.estilo import criar_cabecalho, perguntar_sim_nao


class MenuPrincipalView:
    # Janela inicial do AutoXpert: um botão por módulo.
    # entradas é uma lista de (texto, função). Se a função for None, o módulo ainda
    # não existe e o botão aparece desativado ("em breve").

    def __init__(self, raiz, entradas):
        self.raiz = raiz
        self.entradas = entradas

        self.raiz.title("AutoXpert")
        self.raiz.geometry("440x" + str(150 + 62 * len(entradas)))
        self.raiz.resizable(False, False)

        criar_cabecalho(self.raiz, "AutoXpert")
        ttk.Label(self.raiz, text="Gestão de oficina").pack(pady=(10, 5))

        quadro = ttk.Frame(self.raiz, padding=(30, 5))
        quadro.pack(fill="both", expand=True)

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

    def sair(self):
        if perguntar_sim_nao(self.raiz, "Sair", "Quer mesmo sair do AutoXpert?"):
            self.raiz.destroy()
