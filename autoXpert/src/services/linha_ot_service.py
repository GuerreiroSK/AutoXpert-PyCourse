from src.models.linha_ot_model import LinhaOT


class LinhaOTService:
    # Regras de negócio das linhas de uma OT (RF04, RF13).
    # Uma linha só existe dentro de uma OT, por isso este service usa o
    # OrdemTrabalhoService para confirmar que a OT existe, que ainda pode ser
    # alterada e para guardar o custo total.
    # Não tem SQL (isso é dos repositórios) nem print/input (isso é das views).
    # Os erros de validação são ValueError, com mensagens prontas a mostrar ao utilizador.

    def __init__(self, repo_linha, ot_service):
        self.repo_linha = repo_linha
        self.ot_service = ot_service

    # ---------- Linhas ----------

    # RF04 + RF13: adiciona uma linha e recalcula o custo da OT.
    # Uma linha de peça tem de indicar a peça (rastreabilidade, RNF03);
    # uma linha de mão-de-obra não tem peça.
    def adicionar_linha(self, id_ot, tipo, descricao, quantidade, preco_unitario,
                        horas_trabalhadas=None, id_peca=None):
        ot = self.ot_service.obter_ot(id_ot)
        self.ot_service.garantir_editavel(ot)

        if descricao is None or descricao.strip() == "":
            raise ValueError("A descrição da linha é obrigatória")
        if quantidade is None or quantidade <= 0:
            raise ValueError("A quantidade tem de ser maior que zero")
        if preco_unitario is None or preco_unitario < 0:
            raise ValueError("O preço unitário não pode ser negativo")
        if tipo == LinhaOT.TIPO_PECA and id_peca is None:
            raise ValueError("Uma linha de peça tem de indicar a peça usada")
        if tipo == LinhaOT.TIPO_MAO_OBRA and id_peca is not None:
            raise ValueError("Uma linha de mão-de-obra não pode ter peça")

        linha = LinhaOT(id_ot, tipo, descricao.strip(), quantidade, preco_unitario,
                        horas_trabalhadas=horas_trabalhadas, id_peca=id_peca)
        self.repo_linha.inserir(linha)
        self.recalcular_custo(id_ot)
        return linha

    # Remove uma linha e recalcula o custo da OT
    def remover_linha(self, id_linha):
        linha = self.repo_linha.procurar_por_id(id_linha)
        if linha is None:
            raise ValueError("Linha não encontrada: " + str(id_linha))
        ot = self.ot_service.obter_ot(linha.id_ot)
        self.ot_service.garantir_editavel(ot)
        self.repo_linha.apagar(id_linha)
        self.recalcular_custo(linha.id_ot)

    # RF13: soma o valor de todas as linhas, guarda o total na OT e devolve-o
    def recalcular_custo(self, id_ot):
        total = 0
        for linha in self.repo_linha.listar_por_ot(id_ot):
            total = total + linha.subtotal()
        total = round(total, 2)
        self.ot_service.atualizar_custo_total(id_ot, total)
        return total

    # ---------- Consultas ----------

    # Linhas de uma OT (dá erro se a OT não existir)
    def listar_linhas(self, id_ot):
        self.ot_service.obter_ot(id_ot)
        return self.repo_linha.listar_por_ot(id_ot)
