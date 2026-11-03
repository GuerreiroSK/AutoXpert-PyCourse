from src.services.validacao import texto_obrigatorio, validar_quantidade, validar_valor


class PecaService:
    # Regras das peças e do stock. O SQL fica no repositório (recebido no construtor).

    def __init__(self, peca_repository):
        self.repository = peca_repository

    def listar(self, apenas_stock_baixo=False):
        if apenas_stock_baixo:
            return self.repository.listar_stock_baixo()
        return self.repository.listar_todos()

    def obter(self, id_peca):
        peca = self.repository.obter_por_id(id_peca)
        if peca is None:
            raise ValueError("A peça selecionada já não existe.")
        return peca

    # Cria a peça (sem id) ou atualiza os dados de catálogo (com id).
    # Ao atualizar, o stock atual NÃO muda: para isso há ajustar_stock e receber_stock.
    def guardar(self, peca):
        peca.referencia = texto_obrigatorio(peca.referencia, "Referência")
        peca.nome = texto_obrigatorio(peca.nome, "Nome")
        peca.fornecedor = (peca.fornecedor or "").strip() or None
        validar_valor(peca.preco_compra, "Preço de compra")
        validar_valor(peca.preco_venda, "Preço de venda")
        validar_quantidade(peca.stock_atual, "Stock atual")
        validar_quantidade(peca.stock_minimo, "Stock mínimo")

        if peca.id_peca is None:
            return self.repository.inserir(peca)

        if not self.repository.atualizar(peca):
            raise ValueError("A peça selecionada já não existe.")
        return self.obter(peca.id_peca)

    # variacao positiva = entrada, negativa = saída (nunca deixa o stock negativo)
    def ajustar_stock(self, id_peca, variacao):
        if isinstance(variacao, bool) or not isinstance(variacao, int) or variacao == 0:
            raise ValueError("A variação de stock deve ser um inteiro diferente de zero.")

        peca = self.obter(id_peca)
        if peca.stock_atual + variacao < 0:
            raise ValueError("A saída pedida excede o stock disponível.")

        if not self.repository.atualizar_stock(id_peca, variacao):
            raise ValueError("A peça selecionada já não existe.")
        return self.obter(id_peca)

    # Receção de material: soma ao stock e guarda o fornecedor e o preço de compra
    def receber_stock(self, id_peca, quantidade, fornecedor, preco_compra):
        validar_quantidade(quantidade, "Quantidade recebida")
        if quantidade == 0:
            raise ValueError("A quantidade recebida tem de ser superior a zero.")
        fornecedor = texto_obrigatorio(fornecedor, "Fornecedor")
        validar_valor(preco_compra, "Preço de compra")

        if not self.repository.registar_entrada(id_peca, quantidade, fornecedor,
                                                preco_compra):
            raise ValueError("A peça selecionada já não existe.")
        return self.obter(id_peca)

    def eliminar(self, id_peca):
        if not self.repository.eliminar(id_peca):
            raise ValueError("A peça selecionada já não existe.")
