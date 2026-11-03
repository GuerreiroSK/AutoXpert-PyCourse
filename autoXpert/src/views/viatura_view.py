from tkinter import ttk

from src.views.estilo import (
    criar_janela, criar_cabecalho, texto, pedir_dados, pedir_texto, pedir_inteiro,
    mostrar_erro, mostrar_info, perguntar_sim_nao, mostrar_tabela, mostrar_detalhe
)


class ViaturaView:
    # Janela de gestão de viaturas. O ViaturaController chama estes métodos
    # (pedir_*, mostrar_*, confirmar_*) e trata das regras; a view só desenha.
    #
    # obter_clientes (opcional): função que devolve a lista de clientes. Se existir,
    # o formulário mostra uma lista de escolha em vez de pedir o ID escrito à mão.

    def __init__(self, root, obter_clientes=None):
        self.root = root
        self.obter_clientes = obter_clientes
        self.janela = None

    # Janela por cima da qual os diálogos abrem (o menu, se estiver aberto)
    def pai(self):
        if self.janela is not None and self.janela.winfo_exists():
            return self.janela
        return self.root

    def menu_viatura(self, controller):
        if self.janela is not None and self.janela.winfo_exists():
            self.janela.lift()
            return

        self.janela = criar_janela(self.root, "AutoXpert - Viaturas", 380, 500)
        criar_cabecalho(self.janela, "Gestão de Viaturas")

        corpo = ttk.Frame(self.janela, padding=(30, 15))
        corpo.pack(fill="both", expand=True)

        botoes = [
            ("Registar viatura", controller.registar_viatura),
            ("Consultar viatura", controller.consultar_viatura),
            ("Listar viaturas", controller.listar_viaturas),
            ("Atualizar viatura", controller.atualizar_viatura),
            ("Eliminar viatura", controller.eliminar_viatura),
            ("Consultar histórico", controller.consultar_historico),
        ]
        for texto_botao, comando in botoes:
            ttk.Button(corpo, text=texto_botao, style="Menu.TButton",
                       command=comando).pack(fill="x", pady=4)

        ttk.Button(corpo, text="Fechar", command=self.janela.destroy).pack(pady=(12, 0))

    # ================= Pedidos ao utilizador =================

    def opcoes_clientes(self):
        opcoes = []
        if self.obter_clientes is not None:
            for cliente in self.obter_clientes():
                opcoes.append(str(cliente.id_cliente) + " - " + cliente.nome)
        return opcoes

    def pedir_dados_viatura(self):
        campos = [
            ("matricula", "Matrícula"),
            ("marca", "Marca"),
            ("modelo", "Modelo"),
            ("ano", "Ano"),
            ("cor", "Cor"),
            ("km_entrada", "KM da viatura"),
        ]

        opcoes = self.opcoes_clientes()
        if self.obter_clientes is not None:
            if len(opcoes) == 0:
                mostrar_erro(self.pai(), "Aviso",
                             "Não existem clientes. Registe primeiro um cliente.")
                return None
            campos.append(("id_cliente", "Cliente", opcoes))
        else:
            campos.append(("id_cliente", "ID do cliente"))

        dados = pedir_dados(self.pai(), "Registar viatura", campos, None, "Registar",
                            self.validar_registo)
        if dados is None:
            return None

        resultado = {}
        resultado["matricula"] = dados["matricula"]
        resultado["marca"] = dados["marca"]
        resultado["modelo"] = dados["modelo"]
        resultado["ano"] = self.inteiro_ou_none(dados["ano"])
        resultado["cor"] = dados["cor"] or None
        resultado["km_entrada"] = int(dados["km_entrada"] or "0")
        resultado["id_cliente"] = int(dados["id_cliente"].split(" - ")[0])
        return resultado

    def pedir_matricula(self):
        return pedir_texto(self.pai(), "Consultar viatura", "Matrícula")

    def pedir_id_viatura(self):
        return pedir_inteiro(self.pai(), "Viatura", "ID da viatura")

    def pedir_dados_atualizacao(self, viatura):
        campos = [
            ("matricula", "Matrícula"),
            ("marca", "Marca"),
            ("modelo", "Modelo"),
            ("ano", "Ano"),
            ("cor", "Cor"),
            ("km_entrada", "KM da viatura"),
        ]
        valores = {"matricula": viatura.matricula, "marca": viatura.marca,
                   "modelo": viatura.modelo, "ano": viatura.ano, "cor": viatura.cor,
                   "km_entrada": viatura.km_entrada}

        dados = pedir_dados(self.pai(), "Atualizar viatura " + str(viatura.id_viatura),
                            campos, valores, "Guardar", self.validar_registo)
        if dados is None:
            return None

        return {
            "matricula": dados["matricula"],
            "marca": dados["marca"],
            "modelo": dados["modelo"],
            "ano": self.inteiro_ou_none(dados["ano"]),
            "cor": dados["cor"] or None,
            "km_entrada": int(dados["km_entrada"] or "0"),
        }

    def confirmar_eliminacao(self):
        return perguntar_sim_nao(self.pai(), "Confirmar eliminação",
                                 "Tem a certeza de que pretende eliminar esta viatura?")

    # ================= Resultados =================

    def mostrar_viatura(self, viatura):
        pares = [
            ("ID", viatura.id_viatura),
            ("Matrícula", viatura.matricula),
            ("Marca", viatura.marca),
            ("Modelo", viatura.modelo),
            ("Ano", viatura.ano),
            ("Cor", viatura.cor),
            ("KM da viatura", viatura.km_entrada),
            ("ID do cliente", viatura.id_cliente),
        ]
        mostrar_detalhe(self.pai(), "Dados da viatura", pares)

    def mostrar_viaturas(self, viaturas):
        if not viaturas:
            mostrar_info(self.pai(), "Viaturas", "Não existem viaturas registadas.")
            return

        colunas = [
            ("id", "ID", 50, "center"),
            ("matricula", "Matrícula", 100, "center"),
            ("marca", "Marca", 120, "w"),
            ("modelo", "Modelo", 130, "w"),
            ("ano", "Ano", 60, "center"),
            ("cor", "Cor", 90, "center"),
            ("km", "KM", 90, "e"),
            ("cliente", "Cliente", 70, "center"),
        ]
        linhas = []
        for v in viaturas:
            linhas.append((v.id_viatura, v.matricula, v.marca, v.modelo, texto(v.ano),
                           texto(v.cor), v.km_entrada, v.id_cliente))
        mostrar_tabela(self.pai(), "Lista de viaturas", colunas, linhas, 780, 440)

    def mostrar_historico(self, historico):
        if not historico:
            mostrar_info(self.pai(), "Histórico",
                         "Não existem ordens de trabalho para esta viatura.")
            return

        colunas = [
            ("ot", "OT", 50, "center"),
            ("entrada", "Entrada", 95, "center"),
            ("prev", "Saída prevista", 100, "center"),
            ("saida", "Saída real", 95, "center"),
            ("estado", "Estado", 100, "center"),
            ("avaria", "Avaria", 260, "w"),
            ("custo", "Custo (€)", 80, "e"),
        ]
        linhas = []
        for ot in historico:
            linhas.append((ot.id_ot, ot.data_entrada, ot.data_prev_saida,
                           texto(ot.data_saida_real), ot.estado,
                           ot.descricao_avaria, ot.custo_total))
        mostrar_tabela(self.pai(), "Histórico da viatura", colunas, linhas, 860, 440)

    # O controller chama estes dois com (título, mensagem)
    def mostrar_mensagem(self, titulo, mensagem):
        mostrar_info(self.pai(), titulo, mensagem)

    def mostrar_erro(self, titulo, mensagem):
        mostrar_erro(self.pai(), titulo, mensagem)

    # ================= Auxiliares =================

    def inteiro_ou_none(self, valor):
        if valor == "":
            return None
        return int(valor)

    def validar_registo(self, dados):
        if dados["matricula"] == "":
            return "A matrícula é obrigatória."
        if dados["marca"] == "":
            return "A marca é obrigatória."
        if dados["modelo"] == "":
            return "O modelo é obrigatório."
        if dados["ano"] != "" and not dados["ano"].isdigit():
            return "O ano tem de ser um número inteiro."
        if dados["km_entrada"] != "" and not dados["km_entrada"].isdigit():
            return "Os KM da viatura têm de ser um número inteiro (0 ou mais)."
        if "id_cliente" in dados:
            if not dados["id_cliente"].split(" - ")[0].isdigit():
                return "O ID do cliente tem de ser um número inteiro."
        return None
