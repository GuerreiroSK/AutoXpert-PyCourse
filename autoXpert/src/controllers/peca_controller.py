from src.controllers.conversoes import ler_decimal, ler_inteiro
from src.models.peca import Peca
from src.services.peca_service import PecaService


class PecaController:
    def __init__(self, servico: PecaService):
        self.servico = servico

    def listar(self, apenas_stock_baixo: bool = False) -> list[Peca]:
        return self.servico.listar(apenas_stock_baixo)

    def obter(self, id_peca: int) -> Peca:
        return self.servico.obter(id_peca)

    def guardar(self, dados: dict[str, str], id_peca: int | None = None) -> Peca:
        peca = Peca(
            referencia=dados["referencia"],
            nome=dados["nome"],
            preco_compra=ler_decimal(dados["preco_compra"], "Preco de compra"),
            preco_venda=ler_decimal(dados["preco_venda"], "Preco de venda"),
            stock_atual=ler_inteiro(dados["stock_atual"], "Stock atual"),
            stock_minimo=ler_inteiro(dados["stock_minimo"], "Stock minimo"),
            fornecedor=dados["fornecedor"],
            id_peca=id_peca,
        )
        return self.servico.guardar(peca)

    def ajustar_stock(self, id_peca: int, variacao: str) -> Peca:
        return self.servico.ajustar_stock(id_peca, ler_inteiro(variacao, "Variacao"))

    def receber_stock(
        self, id_peca: int, quantidade: str, fornecedor: str, preco_compra: str,
    ) -> Peca:
        return self.servico.receber_stock(
            id_peca, ler_inteiro(quantidade, "Quantidade recebida"),
            fornecedor, ler_decimal(preco_compra, "Preco de compra"),
        )

    def eliminar(self, id_peca: int) -> None:
        self.servico.eliminar(id_peca)
