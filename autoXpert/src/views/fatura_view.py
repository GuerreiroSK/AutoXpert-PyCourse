import sqlite3
from datetime import date, datetime
from tkinter import ttk

from src.services.validacao import validar_campos

from src.views.estilo import (
    criar_janela, criar_cabecalho, criar_tabela, criar_barra_estado, PesquisaTabela,
    texto, pedir_dados, pedir_inteiro, mostrar_erro, mostrar_info, perguntar_sim_nao,
    texto_do_erro
)

METODOS = ["Dinheiro", "Multibanco", "MB Way", "Transferência"]

COLUNAS = [
    ("id", "Fatura", 60, "center"),
    ("ot", "OT", 60, "center"),
    ("emissao", "Emissão", 100, "center"),
    ("valor", "Valor (€)", 100, "e"),
    ("pago", "Paga", 70, "center"),
    ("data_pag", "Data pagamento", 120, "center"),
    ("metodo", "Método", 130, "center"),
]


class FaturaView:
    # Janela de faturação. Só desenha e recolhe dados:
    # tudo o resto é pedido ao FaturaController.

    def __init__(self, raiz, fatura_controller):
        self.raiz = raiz
        self.controller = fatura_controller
        self.janela = None

    def menu(self):
        if self.janela is not None and self.janela.winfo_exists():
            self.janela.lift()
            return

        self.janela = criar_janela(self.raiz, "AutoXpert - Faturação", 860, 480)
        criar_cabecalho(self.janela, "Faturação")

        barra_botoes = ttk.Frame(self.janela, padding=(10, 10, 10, 0))
        barra_botoes.pack(fill="x")
        ttk.Button(barra_botoes, text="Gerar fatura de uma OT",
                   command=self.gerar_fatura).pack(side="left", padx=(0, 5))
        ttk.Button(barra_botoes, text="Nova fatura manual",
                   command=self.adicionar_fatura).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Marcar como paga",
                   command=self.marcar_paga).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Eliminar",
                   command=self.eliminar_fatura).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Relatório mensal (Excel)",
                   command=self.exportar_relatorio).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Fechar",
                   command=self.janela.destroy).pack(side="right")

        self.barra = criar_barra_estado(self.janela)

        corpo = ttk.Frame(self.janela, padding=10)
        corpo.pack(fill="both", expand=True)

        self.pesquisa = PesquisaTabela(corpo, self.mostrar_contagem)
        self.pesquisa.quadro.pack(fill="x", pady=(0, 8))
        self.tabela = criar_tabela(corpo, COLUNAS, 12)
        self.pesquisa.associar(self.tabela)

        self.listar_faturas()

    # ================= Ações =================

    def listar_faturas(self):
        faturas = self.controller.listar_faturas()
        linhas = []
        for f in faturas:
            if f.pago:
                pago = "Sim"
            else:
                pago = "Não"
            valores = (f.id_fatura, f.id_ot, f.data_emissao, round(f.valor_total, 2),
                       pago, texto(f.data_pagamento), texto(f.metodo_pagamento))
            linhas.append((str(f.id_fatura), valores, ()))
        self.pesquisa.definir_linhas(linhas)

    # Chamada pela PesquisaTabela sempre que a tabela é filtrada
    def mostrar_contagem(self, visiveis, total):
        if total == 0:
            self.barra.set("Não existem faturas registadas.")
        elif self.pesquisa.pesquisa_ativa():
            self.barra.set(str(visiveis) + " de " + str(total) + " fatura(s)")
        else:
            self.barra.set(str(total) + " fatura(s)")

    def gerar_fatura(self):
        id_ot = pedir_inteiro(self.janela, "Gerar fatura", "ID da ordem de trabalho")
        if id_ot is None:
            return

        try:
            fatura = self.controller.gerar_fatura_por_ot(id_ot)
        except (ValueError, sqlite3.IntegrityError) as erro:
            mostrar_erro(self.janela, "Erro", texto_do_erro(erro))
            return

        self.listar_faturas()
        self.barra.set("Fatura gerada! ID: " + str(fatura.id_fatura)
                       + " | Valor: " + str(round(fatura.valor_total, 2)) + " €")

    def adicionar_fatura(self):
        campos = [
            ("id_ot", "ID da OT"),
            ("valor", "Valor total (€)"),
            ("pago", "Paga?", ["Não", "Sim"]),
            ("data_pagamento", "Data pagamento (AAAA-MM-DD)"),
            ("metodo", "Método de pagamento", [""] + METODOS),
        ]
        dados = pedir_dados(self.janela, "Nova fatura", campos, None, "Registar",
                            self.validar_fatura, ["id_ot", "valor"])
        if dados is None:
            return

        if dados["pago"] == "Sim":
            pago = 1
        else:
            pago = 0

        try:
            fatura = self.controller.registar_fatura(
                dados["id_ot"], dados["valor"].replace(",", "."), pago,
                dados["data_pagamento"] or None, dados["metodo"] or None)
        except (ValueError, sqlite3.IntegrityError) as erro:
            mostrar_erro(self.janela, "Erro", texto_do_erro(erro))
            return

        self.listar_faturas()
        self.barra.set("Fatura registada com sucesso! ID: " + str(fatura.id_fatura))

    def marcar_paga(self):
        id_fatura = self.fatura_selecionada()
        if id_fatura is None:
            return

        campos = [
            ("data_pagamento", "Data pagamento (AAAA-MM-DD)"),
            ("metodo", "Método de pagamento", METODOS),
        ]
        valores = {"data_pagamento": date.today().isoformat()}
        dados = pedir_dados(self.janela, "Marcar como paga", campos, valores, "Confirmar",
                            self.validar_data_pagamento, ["data_pagamento"])
        if dados is None:
            return

        try:
            self.controller.marcar_fatura_como_paga(
                id_fatura, dados["data_pagamento"], dados["metodo"])
        except (ValueError, sqlite3.IntegrityError) as erro:
            mostrar_erro(self.janela, "Erro", texto_do_erro(erro))
            return

        self.listar_faturas()
        self.barra.set("Fatura marcada como paga.")

    def eliminar_fatura(self):
        id_fatura = self.fatura_selecionada()
        if id_fatura is None:
            return

        if not perguntar_sim_nao(self.janela, "Eliminar",
                                 "Eliminar a fatura " + str(id_fatura) + "?"):
            return

        try:
            self.controller.eliminar_fatura(id_fatura)
        except (ValueError, sqlite3.IntegrityError) as erro:
            mostrar_erro(self.janela, "Erro", texto_do_erro(erro))
            return

        self.listar_faturas()
        self.barra.set("Fatura eliminada.")

    def exportar_relatorio(self):
        meses = []
        for numero in range(1, 13):
            meses.append(str(numero))
        campos = [
            ("mes", "Mês", meses),
            ("ano", "Ano"),
        ]
        valores = {"mes": str(date.today().month), "ano": str(date.today().year)}
        dados = pedir_dados(self.janela, "Relatório mensal", campos, valores, "Exportar",
                            self.validar_relatorio, ["ano"])
        if dados is None:
            return

        try:
            caminho = self.controller.exportar_relatorio_mensal(
                int(dados["mes"]), int(dados["ano"]))
        except (ValueError, OSError) as erro:
            mostrar_erro(self.janela, "Erro", str(erro))
            return

        mostrar_info(self.janela, "Relatório exportado",
                     "Ficheiro criado em:\n" + str(caminho))
        self.barra.set("Relatório exportado.")

    # ================= Auxiliares =================

    def fatura_selecionada(self):
        escolhidas = self.tabela.selection()
        if len(escolhidas) == 0:
            mostrar_erro(self.janela, "Aviso", "Escolha primeiro uma fatura na lista.")
            return None
        return int(escolhidas[0])

    def validar_fatura(self, dados):
        erros = validar_campos({
            "ID da OT": {"valor": dados["id_ot"], "tipo": "inteiro"},
            "Valor total": {"valor": dados["valor"].replace(",", "."), "tipo": "decimal"},
        })
        if dados["id_ot"].isdigit() and int(dados["id_ot"]) < 1:
            erros.append("O ID da OT tem de ser positivo.")
        try:
            if float(dados["valor"].replace(",", ".")) < 0:
                erros.append("O valor não pode ser negativo.")
        except ValueError:
            pass
        if dados["data_pagamento"]:
            try:
                datetime.strptime(dados["data_pagamento"], "%Y-%m-%d")
            except ValueError:
                erros.append("A data de pagamento deve estar no formato AAAA-MM-DD.")
        if dados["pago"] == "Sim" and dados["metodo"] == "":
            erros.append("Indique o método de pagamento.")
        return "\n".join(erros) if erros else None

    # Marcar como paga: a data é obrigatória e tem de ter o formato certo
    def validar_data_pagamento(self, dados):
        try:
            datetime.strptime(dados["data_pagamento"], "%Y-%m-%d")
        except ValueError:
            return "A data de pagamento deve estar no formato AAAA-MM-DD."
        return None

    def validar_relatorio(self, dados):
        erros = validar_campos({"Ano": {"valor": dados["ano"], "tipo": "inteiro"}})
        if dados["ano"].isdigit() and len(dados["ano"]) != 4:
            erros.append("O ano tem de ter 4 dígitos (ex.: 2026).")
        return "\n".join(erros) if erros else None
