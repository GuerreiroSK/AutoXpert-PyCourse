
import tkinter as tk
from tkinter import ttk

from src.views.estilo import criar_cabecalho, ajustar_janela


class AutenticacaoView:

    def __init__(self, raiz, primeiro_acesso, ao_submeter):
        self.raiz = raiz
        self.primeiro_acesso = primeiro_acesso
        self.ao_submeter = ao_submeter

        self.raiz.title("AutoXpert - Autenticação")
        self.raiz.geometry("420x400")
        self.raiz.resizable(False, False)

        criar_cabecalho(self.raiz, "AutoXpert")

        quadro = ttk.Frame(self.raiz, padding=30)
        quadro.pack(fill="both", expand=True)

        if self.primeiro_acesso:
            self.criar_formulario_primeiro_acesso(quadro)
        else:
            self.criar_formulario_login(quadro)

        self.mensagem_var = tk.StringVar(master=self.raiz)

        ttk.Label(
            quadro,
            textvariable=self.mensagem_var,
            foreground="#c24848",
            wraplength=340
        ).pack(pady=(12, 0))

        ajustar_janela(self.raiz, 420, 400)

    def criar_formulario_login(self, quadro):
        ttk.Label(
            quadro,
            text="Iniciar sessão",
            style="Destaque.TLabel"
        ).pack(pady=(0, 20))

        ttk.Label(quadro, text="Utilizador").pack(anchor="w")

        self.login_var = tk.StringVar(master=self.raiz)
        ttk.Entry(
            quadro,
            textvariable=self.login_var
        ).pack(fill="x", pady=(3, 12))

        ttk.Label(quadro, text="Palavra-passe").pack(anchor="w")

        self.senha_var = tk.StringVar(master=self.raiz)
        entrada_senha = ttk.Entry(
            quadro,
            textvariable=self.senha_var,
            show="*"
        )
        entrada_senha.pack(fill="x", pady=(3, 20))

        ttk.Button(
            quadro,
            text="Iniciar sessão",
            command=self.submeter
        ).pack(fill="x")

        entrada_senha.bind(
            "<Return>",
            lambda evento: self.submeter()
        )

    def criar_formulario_primeiro_acesso(self, quadro):
        ttk.Label(
            quadro,
            text="Criar administrador inicial",
            style="Destaque.TLabel"
        ).pack(pady=(0, 15))

        ttk.Label(quadro, text="Nome de utilizador").pack(anchor="w")

        self.login_var = tk.StringVar(master=self.raiz)
        ttk.Entry(
            quadro,
            textvariable=self.login_var
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(quadro, text="Palavra-passe").pack(anchor="w")

        self.senha_var = tk.StringVar(master=self.raiz)
        ttk.Entry(
            quadro,
            textvariable=self.senha_var,
            show="*"
        ).pack(fill="x", pady=(3, 10))

        ttk.Label(quadro, text="Confirmar palavra-passe").pack(anchor="w")

        self.confirmacao_var = tk.StringVar(master=self.raiz)
        entrada_confirmacao = ttk.Entry(
            quadro,
            textvariable=self.confirmacao_var,
            show="*"
        )
        entrada_confirmacao.pack(fill="x", pady=(3, 15))

        ttk.Button(
            quadro,
            text="Criar administrador",
            command=self.submeter
        ).pack(fill="x")

        entrada_confirmacao.bind(
            "<Return>",
            lambda evento: self.submeter()
        )

    def submeter(self):
        login = self.login_var.get().strip()
        senha = self.senha_var.get()

        if self.primeiro_acesso:
            confirmacao = self.confirmacao_var.get()
        else:
            confirmacao = None

        self.ao_submeter(login, senha, confirmacao)

    def mostrar_mensagem(self, mensagem):
        self.mensagem_var.set(mensagem)

    def limpar_campos(self):
        self.login_var.set("")
        self.senha_var.set("")

        if self.primeiro_acesso:
            self.confirmacao_var.set("")
