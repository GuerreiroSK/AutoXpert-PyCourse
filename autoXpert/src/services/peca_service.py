from src.models.peca import Peca
from src.repositories import pecas_repository as repository
from src.services.validacao import texto_obrigatorio, validar_quantidade, validar_valor


class PecaService:
    def listar(self, apenas_stock_baixo: bool = False) -> list[Peca]:
        if apenas_stock_baixo:
            linhas = repository.listar_pecas_com_stock_baixo()
        else:
            linhas = repository.listar_pecas()

        pecas: list[Peca] = []

        for linha in linhas:
            peca = Peca.da_linha(linha)
            pecas.append(peca)

        return pecas

    def obter(self, id_peca: int) -> Peca:
        linha = repository.obter_peca(id_peca)
        if linha is None:
            raise ValueError("A peca selecionada ja nao existe.")
        return Peca.da_linha(linha)

    def guardar(self, peca: Peca) -> Peca:
        referencia = texto_obrigatorio(peca.referencia, "Referencia")
        nome = texto_obrigatorio(peca.nome, "Nome")
        fornecedor = (peca.fornecedor or "").strip() or None
        validar_valor(peca.preco_compra, "Preco de compra")
        validar_valor(peca.preco_venda, "Preco de venda")
        validar_quantidade(peca.stock_atual, "Stock atual")
        validar_quantidade(peca.stock_minimo, "Stock minimo")

        if peca.id_peca is None:
            id_peca = repository.criar_peca(
                referencia, nome, peca.preco_compra, peca.preco_venda,
                peca.stock_atual, peca.stock_minimo, fornecedor,
            )
        else:
            id_peca = peca.id_peca
            atualizado = repository.atualizar_peca(
                id_peca, referencia, nome, peca.stock_minimo,
                peca.preco_compra, peca.preco_venda, fornecedor,
            )
            if not atualizado:
                raise ValueError("A peca selecionada ja nao existe.")
        return self.obter(id_peca)

    def ajustar_stock(self, id_peca: int, variacao: int) -> Peca:
        if isinstance(variacao, bool) or not isinstance(variacao, int) or variacao == 0:
            raise ValueError("A variacao de stock deve ser um inteiro diferente de zero.")
        peca = self.obter(id_peca)
        if peca.stock_atual + variacao < 0:
            raise ValueError("A saida pedida excede o stock disponivel.")
        if not repository.atualizar_stock(id_peca, variacao):
            raise ValueError("A peca selecionada ja nao existe.")
        return self.obter(id_peca)

    def receber_stock(
        self, id_peca: int, quantidade: int, fornecedor: str, preco_compra: float,
    ) -> Peca:
        validar_quantidade(quantidade, "Quantidade recebida")
        if quantidade == 0:
            raise ValueError("A quantidade recebida tem de ser superior a zero.")
        fornecedor = texto_obrigatorio(fornecedor, "Fornecedor")
        validar_valor(preco_compra, "Preco de compra")
        if not repository.registar_entrada_stock(id_peca, quantidade, fornecedor, preco_compra):
            raise ValueError("A peca selecionada ja nao existe.")
        return self.obter(id_peca)

    def eliminar(self, id_peca: int) -> None:
        if not repository.eliminar_peca(id_peca):
            raise ValueError("A peca selecionada ja nao existe.")
