import sqlite3
import csv
import tkinter as tk
from pathlib import Path
from datetime import date, datetime
from tkinter import ttk, messagebox


from src.services.validacao import validar_campos

from src.views.tema import tags_linha_alternada
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

        self.janela = criar_janela(self.raiz, "AutoXpert - Faturação", 1300, 650)
        criar_cabecalho(self.janela, "Faturação")

        barra_botoes = ttk.Frame(self.janela, padding=(10, 10, 10, 0))
        barra_botoes.pack(fill="x")
        ttk.Button(barra_botoes, text="Gerar fatura de uma OT",
                   command=self.gerar_fatura).pack(side="left", padx=(0, 5))
        ttk.Button(barra_botoes, text="Nova fatura manual",
                   command=self.adicionar_fatura).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Marcar como paga",
                   command=self.marcar_paga).pack(side="left", padx=5)
        # Abre a janela com os dados completos da fatura selecionada.
        ttk.Button(barra_botoes, text="Ver detalhe",
                   command=self.ver_detalhe).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Eliminar", style="Perigo.TButton",
                   command=self.eliminar_fatura).pack(side="left", padx=5)
        ttk.Button(barra_botoes, text="Relatório mensal (Excel)",
                   command=self.exportar_relatorio).pack(side="left", padx=5)
        # Botão para exportar as faturas apresentadas na tabela.
        ttk.Button(barra_botoes, text="Exportar CSV",
                   command=self.exportar_csv).pack(side="left", padx=5)
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
            self.tabela.insert("", "end", iid=str(f.id_fatura), values=(
                f.id_fatura, f.id_ot, f.data_emissao, round(f.valor_total, 2), pago,
                texto(f.data_pagamento), texto(f.metodo_pagamento)),
                tags=tags_linha_alternada(self.tabela))
        if len(faturas) == 0:
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

    # Exporta para CSV as faturas apresentadas na tabela.
    def exportar_csv(self):
        # Define a pasta docs na raiz do projeto.
        pasta_docs = Path(__file__).resolve().parents[2] / "docs"
        pasta_docs.mkdir(parents=True, exist_ok=True)

        # Cria um nome com data e hora para evitar substituir ficheiros.
        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho = pasta_docs / f"faturacao_{data_hora}.csv"

        # Obtém os cabeçalhos das colunas da tabela.
        cabecalho = [coluna[1] for coluna in COLUNAS]

        try:
            # Escreve os cabeçalhos e os dados da tabela no ficheiro.
            with open(caminho, "w", newline="", encoding="utf-8-sig") as ficheiro:
                escritor = csv.writer(ficheiro, delimiter=";")
                escritor.writerow(cabecalho)

                for item in self.tabela.get_children():
                    valores = self.tabela.item(item, "values")
                    escritor.writerow(valores)

        except OSError as erro:
            messagebox.showerror("Erro", str(erro), parent=self.janela)
            return

        # Informa o utilizador de que a exportação foi concluída.
        messagebox.showinfo(
            "Exportação concluída",
            f"Ficheiro CSV criado em:\n{caminho}",
            parent=self.janela
        )
        self.barra.set("Faturação exportada para CSV.")

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

    # Cria um campo de informação com o respetivo título e valor.
    def criar_campo_detalhe(self, quadro, titulo, valor, linha, coluna):
        ttk.Label(
            quadro,
            text=titulo + ":",
            font=("TkDefaultFont", 9, "bold")
        ).grid(row=linha, column=coluna, padx=8, pady=5, sticky="e")

        ttk.Label(
            quadro,
            text=str(valor) if valor is not None else "-",
            wraplength=300
        ).grid(row=linha, column=coluna + 1, padx=8, pady=5, sticky="w")

    # Abre uma janela com os dados completos da fatura selecionada.
    def ver_detalhe(self):
        id_fatura = self.fatura_selecionada()

        if id_fatura is None:
            return

        # Obtém a fatura, as linhas da OT e os totais calculados.
        try:
            detalhe = self.controller.consultar_detalhe(id_fatura)
        except (ValueError, sqlite3.Error) as erro:
            mostrar_erro(self.janela, "Erro", texto_do_erro(erro))
            return

        fatura = detalhe["fatura"]
        linhas = detalhe["linhas"]

        # Cria a janela secundária.
        janela = tk.Toplevel(self.janela)
        janela.title("Detalhe da Fatura " + str(fatura.id_fatura))
        janela.geometry("850x650")
        janela.transient(self.janela)
        janela.protocol("WM_DELETE_WINDOW", janela.destroy)

        # Apresenta a identificação e os dados principais da fatura.
        quadro_fatura = ttk.LabelFrame(janela, text="Dados da Fatura")
        quadro_fatura.pack(fill="x", padx=10, pady=8)

        self.criar_campo_detalhe(
            quadro_fatura, "N.º Fatura", fatura.id_fatura, 0, 0
        )
        self.criar_campo_detalhe(
            quadro_fatura, "Ordem de Trabalho", fatura.id_ot, 0, 2
        )
        self.criar_campo_detalhe(
            quadro_fatura, "Data de emissão", fatura.data_emissao, 1, 0
        )

        # Apresenta os serviços e as peças associados à OT.
        quadro_linhas = ttk.LabelFrame(janela, text="Serviços e Peças")
        quadro_linhas.pack(fill="both", expand=True, padx=10, pady=5)

        colunas = (
            "tipo", "descricao", "quantidade", "horas",
            "preco", "subtotal"
        )

        tabela = ttk.Treeview(
            quadro_linhas,
            columns=colunas,
            show="headings",
            height=8
        )

        titulos = [
            ("tipo", "Tipo", 100),
            ("descricao", "Descrição", 260),
            ("quantidade", "Quantidade", 85),
            ("horas", "Horas", 75),
            ("preco", "Preço unit. (€)", 110),
            ("subtotal", "Subtotal (€)", 110)
        ]

        for coluna, titulo, largura in titulos:
            tabela.heading(coluna, text=titulo)
            tabela.column(coluna, width=largura, anchor="center")

        tabela.pack(fill="both", expand=True, padx=5, pady=5)

        # Insere as linhas da OT na tabela.
        for linha in linhas:
            if linha["tipo"] == "mao_obra":
                tipo = "Mão-de-obra"
            elif linha["tipo"] == "peca":
                tipo = "Peça"
            else:
                tipo = linha["tipo"]

            tabela.insert("", "end", values=(
                tipo,
                linha["descricao"],
                linha["quantidade"],
                texto(linha["horas_trabalhadas"]),
                round(linha["preco_unitario"], 2),
                round(linha["subtotal"], 2)
            ))

        if len(linhas) == 0:
            tabela.insert(
                "", "end",
                values=("", "Sem serviços ou peças registados", "", "", "", "")
            )

        # Apresenta os totais calculados e o valor registado na fatura.
        quadro_totais = ttk.LabelFrame(janela, text="Totais")
        quadro_totais.pack(fill="x", padx=10, pady=5)

        self.criar_campo_detalhe(
            quadro_totais, "Total mão-de-obra",
            str(detalhe["total_mao_obra"]) + " €", 0, 0
        )
        self.criar_campo_detalhe(
            quadro_totais, "Total peças",
            str(detalhe["total_pecas"]) + " €", 0, 2
        )
        self.criar_campo_detalhe(
            quadro_totais, "Valor total da fatura",
            str(round(fatura.valor_total, 2)) + " €", 1, 0
        )

        # Apresenta o estado e os dados do pagamento.
        quadro_pagamento = ttk.LabelFrame(janela, text="Pagamento")
        quadro_pagamento.pack(fill="x", padx=10, pady=5)

        if fatura.pago:
            estado_pagamento = "Paga"
        else:
            estado_pagamento = "Por pagar"

        self.criar_campo_detalhe(
            quadro_pagamento, "Estado", estado_pagamento, 0, 0
        )
        self.criar_campo_detalhe(
            quadro_pagamento, "Data de pagamento",
            texto(fatura.data_pagamento), 0, 2
        )
        self.criar_campo_detalhe(
            quadro_pagamento, "Método de pagamento",
            texto(fatura.metodo_pagamento), 1, 0
        )

        # Botão para fechar a janela de detalhe.
        ttk.Button(
            janela,
            text="Fechar",
            command=janela.destroy
        ).pack(pady=10)

