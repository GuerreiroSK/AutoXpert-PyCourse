class Peca:

    def __init__(self, referencia, nome, preco_compra, preco_venda,
                 stock_atual=0, stock_minimo=0, fornecedor=None, id_peca=None):
        self.id_peca = id_peca
        self.referencia = referencia
        self.nome = nome
        self.preco_compra = preco_compra
        self.preco_venda = preco_venda
        self.stock_atual = stock_atual
        self.stock_minimo = stock_minimo
        self.fornecedor = fornecedor

    # True se o stock já chegou (ou desceu abaixo do mínimo
    def stock_baixo(self):
        return self.stock_atual <= self.stock_minimo

    def __str__(self):
        return "Peça " + str(self.id_peca) + ": " + self.nome
