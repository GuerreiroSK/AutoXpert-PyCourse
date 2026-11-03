import sqlite3
from tkinter import ttk

from src.views.estilo import (
    criar_janela, criar_cabecalho, criar_tabela, limpar_tabela, criar_barra_estado,
    texto, pedir_dados, mostrar_erro, perguntar_sim_nao, texto_do_erro
)

CAMPOS = [
    ("nome", "Nome"),
    ("nif", "NIF"),
    ("telefone", "Telefone"),
    ("email", "Email"),
    ("morada", "Morada"),
]

COLUNAS = [
    ("id", "ID", 50, "center"),
    ("nome", "Nome", 200, "w"),
    ("nif", "NIF", 100, "center"),
    ("telefone", "Telefone", 110, "center"),
    ("email", "Email", 190, "w"),
    ("morada", "Morada", 220, "w"),
    ("data", "Registo", 100, "center"),
]


class ClienteView:
    # Janela de gestão de clientes. Só desenha e recolhe dados:
    # tudo o resto é pedido ao ClienteController.

    def __init__(self, raiz, cliente_controller):
        self.raiz = raiz
        self.controller = cliente_controller
        self.janela = None

    def menu(self):
        # Se a janela já estiver aberta, traz-a para a frente
        if self.janela is not None and self.janela.winfo_exists():
            self.janela.lift()
            return

        self.janela = criar_janela(self.raiz, "AutoXpert - Clientes", 1020, 480)
        criar_cabecalho(self.janela, "Gestão de Clientes")

        barra_botoes = ttk.Frame(self.janela, padding=(10, 10, 10, 0))
        barra_botoes.pack(fill="x")
        ttk.Button(barra_botoes, text="Novo cliente",
                   command=self.adicionar_cliente).pack(side="left", padx=(0, 5))
        ttk.Button(barra_botoes, text="Editar",
                   command=self.editar_cliente).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Eliminar",
                   command=self.eliminar_cliente).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Atualizar lista",
                   command=self.listar_clientes).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Fechar",
                   command=self.janela.destroy).pack(side="right")

        self.barra = criar_barra_estado(self.janela)

        corpo = ttk.Frame(self.janela, padding=10)
        corpo.pack(fill="both", expand=True)
        self.tabela = criar_tabela(corpo, COLUNAS, 12)

        self.listar_clientes()

    # ================= Ações =================

    def listar_clientes(self):
        limpar_tabela(self.tabela)
        clientes = self.controller.listar_clientes()
        for c in clientes:
            self.tabela.insert("", "end", iid=str(c.id_cliente), values=(
                c.id_cliente, c.nome, texto(c.nif), texto(c.telefone),
                texto(c.email), texto(c.morada), texto(c.data_registo)))
        if len(clientes) == 0:
            self.barra.set("Não existem clientes registados.")
        else:
            self.barra.set(str(len(clientes)) + " cliente(s)")

    def adicionar_cliente(self):
        dados = pedir_dados(self.janela, "Novo cliente", CAMPOS, None, "Registar",
                            self.validar)
        if dados is None:
            return

        try:
            cliente = self.controller.registar_cliente(
                dados["nome"], dados["nif"], dados["telefone"],
                dados["email"], dados["morada"])
        except (ValueError, sqlite3.IntegrityError) as erro:
            mostrar_erro(self.janela, "Erro", texto_do_erro(erro))
            return

        self.listar_clientes()
        self.barra.set("Cliente registado com sucesso! ID: " + str(cliente.id_cliente))

    def editar_cliente(self):
        id_cliente = self.cliente_selecionado()
        if id_cliente is None:
            return

        try:
            cliente = self.controller.consultar_cliente(id_cliente)
        except ValueError as erro:
            mostrar_erro(self.janela, "Erro", str(erro))
            self.listar_clientes()
            return

        valores = {"nome": cliente.nome, "nif": cliente.nif, "telefone": cliente.telefone,
                   "email": cliente.email, "morada": cliente.morada}
        dados = pedir_dados(self.janela, "Editar cliente " + str(id_cliente), CAMPOS,
                            valores, "Guardar", self.validar)
        if dados is None:
            return

        cliente.nome = dados["nome"]
        cliente.nif = dados["nif"] or None
        cliente.telefone = dados["telefone"] or None
        cliente.email = dados["email"] or None
        cliente.morada = dados["morada"] or None
        try:
            self.controller.atualizar_cliente(cliente)
        except (ValueError, sqlite3.IntegrityError) as erro:
            mostrar_erro(self.janela, "Erro", texto_do_erro(erro))
            return

        self.listar_clientes()
        self.barra.set("Cliente atualizado.")

    def eliminar_cliente(self):
        id_cliente = self.cliente_selecionado()
        if id_cliente is None:
            return

        if not perguntar_sim_nao(self.janela, "Eliminar",
                                 "Eliminar o cliente " + str(id_cliente) + "?"):
            return

        try:
            self.controller.eliminar_cliente(id_cliente)
        except (ValueError, sqlite3.IntegrityError) as erro:
            mostrar_erro(self.janela, "Erro", texto_do_erro(erro))
            return

        self.listar_clientes()
        self.barra.set("Cliente eliminado.")

    # ================= Auxiliares =================

    # ID do cliente escolhido na tabela (ou None, com aviso)
    def cliente_selecionado(self):
        escolhidos = self.tabela.selection()
        if len(escolhidos) == 0:
            mostrar_erro(self.janela, "Aviso", "Escolha primeiro um cliente na lista.")
            return None
        return int(escolhidos[0])

    def validar(self, dados):
        if dados["nome"] == "":
            return "O nome é obrigatório."
        if len(dados["telefone"]) > 20:
            return "O telefone não pode ter mais de 20 caracteres."
        return None
