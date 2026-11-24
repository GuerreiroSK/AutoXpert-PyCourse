from src.controllers.conversoes import ler_decimal, ler_inteiro
from src.models.peca_model import Peca
from src.rbac import require_perfil


class PecaController:
    # Converte o texto do formulário em dados para o service.

    def __init__(self, servico, token=None):
        self.servico = servico
        self.token = token

    def perfil_atual(self):
        from src.rbac import obter_perfil
        return obter_perfil(self.token)

    @require_perfil("administrador", "rececionista", "tecnico")
    def listar(self, apenas_stock_baixo=False):
        return self.servico.listar(apenas_stock_baixo)

    @require_perfil("administrador", "rececionista", "tecnico")
    def obter(self, id_peca):
        return self.servico.obter(id_peca)

    # Criar ou atualizar peça.
    @require_perfil("administrador", "rececionista", "tecnico")
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

    @require_perfil("administrador", "rececionista", "tecnico")
    def ajustar_stock(self, id_peca, variacao):
        return self.servico.ajustar_stock(
            id_peca,
            ler_inteiro(variacao, "Variação")
        )

    @require_perfil("administrador", "rececionista", "tecnico")
    def receber_stock(self, id_peca, quantidade, fornecedor, preco_compra):
        return self.servico.receber_stock(
            id_peca,
            ler_inteiro(quantidade, "Quantidade recebida"),
            fornecedor,
            ler_decimal(preco_compra, "Preço de compra")
        )

    @require_perfil("administrador", "rececionista", "tecnico")
    def eliminar(self, id_peca):
        self.servico.eliminar(id_peca)
