from src.controllers.conversoes import ler_decimal, ler_inteiro
from src.models.peca_model import Peca


class PecaController:
    # Converte o texto do formulário em dados para o service.

    def __init__(self, servico):
        self.servico = servico

    def listar(self, apenas_stock_baixo=False):
        return self.servico.listar(apenas_stock_baixo)

    def obter(self, id_peca):
        return self.servico.obter(id_peca)

    # dados é um dicionário com o texto dos campos do formulário
    def guardar(self, dados, id_peca=None):
        peca = Peca(
            referencia=dados["referencia"],
            nome=dados["nome"],
            preco_compra=ler_decimal(dados["preco_compra"], "Preço de compra"),
            preco_venda=ler_decimal(dados["preco_venda"], "Preço de venda"),
            stock_atual=ler_inteiro(dados["stock_atual"], "Stock atual"),
            stock_minimo=ler_inteiro(dados["stock_minimo"], "Stock mínimo"),
            fornecedor=dados["fornecedor"],
            id_peca=id_peca
        )
        return self.servico.guardar(peca)

    def ajustar_stock(self, id_peca, variacao):
        return self.servico.ajustar_stock(id_peca, ler_inteiro(variacao, "Variação"))

    def receber_stock(self, id_peca, quantidade, fornecedor, preco_compra):
        return self.servico.receber_stock(
            id_peca,
            ler_inteiro(quantidade, "Quantidade recebida"),
            fornecedor,
            ler_decimal(preco_compra, "Preço de compra")
        )

    def eliminar(self, id_peca):
        self.servico.eliminar(id_peca)
