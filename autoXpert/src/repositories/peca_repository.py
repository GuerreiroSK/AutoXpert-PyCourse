from src.models.peca_model import Peca


class PecaRepository:
    # Todo o SQL da tabela Peca. A ligação é recebida de fora (como nos outros
    # repositórios) e tem de devolver linhas acessíveis pelo nome da coluna.

    def __init__(self, conexao):
        self.conexao = conexao

    # Converte uma linha da base de dados num objeto Peca
    def _linha_para_objeto(self, linha):
        return Peca(
            referencia=linha["referencia"],
            nome=linha["nome"],
            preco_compra=linha["preco_compra"],
            preco_venda=linha["preco_venda"],
            stock_atual=linha["stock_atual"],
            stock_minimo=linha["stock_minimo"],
            fornecedor=linha["fornecedor"],
            id_peca=linha["id_peca"]
        )

    def _listar_com_sql(self, sql):
        pecas = []
        for linha in self.conexao.execute(sql).fetchall():
            pecas.append(self._linha_para_objeto(linha))
        return pecas

    # Grava a peça e preenche o id gerado pela base de dados
    def inserir(self, peca):
        cursor = self.conexao.execute(
            "INSERT INTO Peca (referencia, nome, stock_atual, stock_minimo, "
            "preco_compra, preco_venda, fornecedor) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (peca.referencia, peca.nome, peca.stock_atual, peca.stock_minimo,
             peca.preco_compra, peca.preco_venda, peca.fornecedor)
        )
        self.conexao.commit()
        peca.id_peca = cursor.lastrowid
        return peca

    def listar_todas(self):
        return self._listar_com_sql("SELECT * FROM Peca ORDER BY nome, id_peca")

    def listar_stock_baixo(self):
        return self._listar_com_sql(
            "SELECT * FROM Peca WHERE stock_atual <= stock_minimo "
            "ORDER BY nome, id_peca")

    # Devolve a peça ou None se o id não existir
    def obter_por_id(self, id_peca):
        linha = self.conexao.execute(
            "SELECT * FROM Peca WHERE id_peca = ?",
            (id_peca,)
        ).fetchone()

        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    def obter_por_referencia(self, referencia):
        linha = self.conexao.execute(
            "SELECT * FROM Peca WHERE referencia = ?",
            (referencia,)
        ).fetchone()

        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    # Atualiza os dados de catálogo. O stock atual não muda aqui (ver atualizar_stock).
    # Devolve True se a peça existia.
    def atualizar(self, peca):
        cursor = self.conexao.execute(
            "UPDATE Peca SET referencia = ?, nome = ?, stock_minimo = ?, "
            "preco_compra = ?, preco_venda = ?, fornecedor = ? WHERE id_peca = ?",
            (peca.referencia, peca.nome, peca.stock_minimo, peca.preco_compra,
             peca.preco_venda, peca.fornecedor, peca.id_peca)
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    # variacao positiva soma ao stock, negativa subtrai. Devolve True se a peça existia.
    def atualizar_stock(self, id_peca, variacao):
        cursor = self.conexao.execute(
            "UPDATE Peca SET stock_atual = stock_atual + ? WHERE id_peca = ?",
            (variacao, id_peca)
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    # Receção de material: soma ao stock e guarda o último fornecedor e preço de compra.
    # Devolve True se a peça existia.
    def registar_entrada(self, id_peca, quantidade, fornecedor, preco_compra):
        if quantidade <= 0:
            raise ValueError("A quantidade recebida tem de ser superior a zero.")

        cursor = self.conexao.execute(
            "UPDATE Peca SET stock_atual = stock_atual + ?, fornecedor = ?, "
            "preco_compra = ? WHERE id_peca = ?",
            (quantidade, fornecedor, preco_compra, id_peca)
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    # Devolve True se a peça existia
    def eliminar(self, id_peca):
        cursor = self.conexao.execute(
            "DELETE FROM Peca WHERE id_peca = ?",
            (id_peca,)
        )
        self.conexao.commit()
        return cursor.rowcount > 0
