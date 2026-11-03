from tkinter import ttk

from src.views.estilo import (
    criar_janela, criar_cabecalho, texto, pedir_dados, pedir_inteiro,
    mostrar_erro, mostrar_info, mostrar_tabela, mostrar_detalhe
)


class LogAlteracaoOTView:
    # Janela do registo de alterações das ordens de trabalho.
    # O LogAlteracaoOTController chama estes métodos; a view só desenha.

    def __init__(self, root):
        self.root = root
        self.janela = None

    def pai(self):
        if self.janela is not None and self.janela.winfo_exists():
            return self.janela
        return self.root

    def menu_log(self, controller):
        if self.janela is not None and self.janela.winfo_exists():
            self.janela.lift()
            return

        self.janela = criar_janela(self.root, "AutoXpert - Registo de alterações", 400, 410)
        criar_cabecalho(self.janela, "Registo de Alterações das OTs")

        corpo = ttk.Frame(self.janela, padding=(30, 15))
        corpo.pack(fill="both", expand=True)

        botoes = [
            ("Registar alteração", controller.registar_alteracao),
            ("Consultar alteração por ID", controller.consultar_alteracao),
            ("Listar alterações de uma OT", controller.listar_alteracoes_por_ot),
            ("Listar todas as alterações", controller.listar_todas_alteracoes),
        ]
        for texto_botao, comando in botoes:
            ttk.Button(corpo, text=texto_botao, style="Menu.TButton",
                       command=comando).pack(fill="x", pady=4)

        ttk.Button(corpo, text="Fechar", command=self.janela.destroy).pack(pady=(12, 0))

    # ================= Pedidos ao utilizador =================

    def pedir_dados_alteracao(self):
        campos = [
            ("id_ot", "ID da ordem de trabalho"),
            ("campo", "Campo alterado"),
            ("valor_anterior", "Valor anterior (opcional)"),
            ("valor_novo", "Novo valor"),
        ]
        dados = pedir_dados(self.pai(), "Registar alteração", campos, None, "Registar",
                            self.validar)
        if dados is None:
            return None

        return {
            "id_ot": int(dados["id_ot"]),
            "campo_alterado": dados["campo"],
            "valor_anterior": dados["valor_anterior"] or None,
            "valor_novo": dados["valor_novo"],
        }

    def pedir_id_log(self):
        return pedir_inteiro(self.pai(), "Consultar alteração", "ID do registo")

    def pedir_id_ot(self):
        return pedir_inteiro(self.pai(), "Consultar alterações", "ID da ordem de trabalho")

    # ================= Resultados =================

    def mostrar_alteracao(self, registo):
        pares = [
            ("ID do registo", registo.id_log),
            ("Ordem de trabalho", registo.id_ot),
            ("Data e hora", registo.data_hora),
            ("Campo alterado", registo.campo_alterado),
            ("Valor anterior", registo.valor_anterior),
            ("Novo valor", registo.valor_novo),
        ]
        mostrar_detalhe(self.pai(), "Detalhes da alteração", pares)

    def mostrar_alteracoes(self, registos):
        if not registos:
            mostrar_info(self.pai(), "Alterações", "Não existem alterações registadas.")
            return

        colunas = [
            ("id", "ID", 50, "center"),
            ("ot", "OT", 50, "center"),
            ("data", "Data e hora", 150, "center"),
            ("campo", "Campo", 130, "w"),
            ("anterior", "Valor anterior", 150, "w"),
            ("novo", "Novo valor", 150, "w"),
        ]
        linhas = []
        for r in registos:
            linhas.append((r.id_log, r.id_ot, r.data_hora, r.campo_alterado,
                           texto(r.valor_anterior), texto(r.valor_novo)))
        mostrar_tabela(self.pai(), "Lista de alterações", colunas, linhas, 760, 420)

    # O controller chama estes dois só com a mensagem
    def mostrar_mensagem(self, mensagem):
        mostrar_info(self.pai(), "Informação", mensagem)

    def mostrar_erro(self, mensagem):
        mostrar_erro(self.pai(), "Erro", mensagem)

    # ================= Auxiliares =================

    def validar(self, dados):
        if not dados["id_ot"].isdigit() or int(dados["id_ot"]) < 1:
            return "O ID da ordem de trabalho tem de ser um número inteiro positivo."
        if dados["campo"] == "":
            return "Indique o campo alterado."
        if dados["valor_novo"] == "":
            return "Indique o novo valor."
        return None
