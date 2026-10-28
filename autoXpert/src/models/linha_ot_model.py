class LinhaOT:
    
    # Tipos possíveis de linha (RF04). Têm de ser iguais aos do CHECK da tabela.
    TIPO_MAO_OBRA = "mao_obra"
    TIPO_PECA = "peca"

    TIPOS = [TIPO_MAO_OBRA, TIPO_PECA]

    def __init__(self, id_ot, tipo, descricao, quantidade, preco_unitario,
                 horas_trabalhadas=None, id_peca=None, id_linha=None):
        if tipo not in LinhaOT.TIPOS:
            raise ValueError("Tipo de linha inválido: " + str(tipo))

        self.id_linha = id_linha
        self.id_ot = id_ot
        self.tipo = tipo
        self.descricao = descricao
        self.quantidade = quantidade
        self.horas_trabalhadas = horas_trabalhadas
        self.preco_unitario = preco_unitario
        self.id_peca = id_peca

    # Valor desta linha (quantidade x preço unitário), usado para somar o custo da OT
    def subtotal(self):
        return round(self.quantidade * self.preco_unitario, 2)

    def __str__(self):
        return ("Linha " + str(self.id_linha) + " (OT " + str(self.id_ot) + ")"
                + " | " + str(self.tipo) + " | " + str(self.descricao)
                + " | qtd: " + str(self.quantidade)
                + " | preço: " + str(self.preco_unitario))