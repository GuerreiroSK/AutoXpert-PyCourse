from src.models.fatura_model import Fatura


class FaturaRepository:
    # Todo o SQL da tabela Fatura. A ligação é recebida de fora (como nos outros
    # repositórios).

    def __init__(self, conexao):
        self.conexao = conexao

    # Converte uma linha da base de dados num objeto Fatura
    def _linha_para_objeto(self, linha):
        return Fatura(
            id_fatura=linha["id_fatura"],
            id_ot=linha["id_ot"],
            data_emissao=linha["data_emissao"],
            valor_total=linha["valor_total"],
            pago=linha["pago"],
            data_pagamento=linha["data_pagamento"],
            metodo_pagamento=linha["metodo_pagamento"]
        )

    def _lista_de_objetos(self, linhas):
        faturas = []
        for linha in linhas:
            faturas.append(self._linha_para_objeto(linha))
        return faturas

    # CREATE - grava a fatura e preenche o id gerado pela base de dados
    def inserir(self, fatura):
        cursor = self.conexao.execute(
            "INSERT INTO Fatura (id_ot, data_emissao, valor_total, pago, "
            "data_pagamento, metodo_pagamento) VALUES (?, ?, ?, ?, ?, ?)",
            (fatura.id_ot, fatura.data_emissao, fatura.valor_total, fatura.pago,
             fatura.data_pagamento, fatura.metodo_pagamento)
        )
        self.conexao.commit()
        fatura.id_fatura = cursor.lastrowid
        return fatura

    # READ - todas as faturas
    def listar_todos(self):
        linhas = self.conexao.execute(
            "SELECT * FROM Fatura ORDER BY id_fatura"
        ).fetchall()
        return self._lista_de_objetos(linhas)

    # READ - uma fatura pelo ID (ou None)
    def obter_por_id(self, id_fatura):
        linha = self.conexao.execute(
            "SELECT * FROM Fatura WHERE id_fatura = ?",
            (id_fatura,)
        ).fetchone()

        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    # READ - a fatura de uma OT (ou None). O service usa-o para não criar duas
    # faturas para a mesma OT.
    def obter_por_ot(self, id_ot):
        linha = self.conexao.execute(
            "SELECT * FROM Fatura WHERE id_ot = ?",
            (id_ot,)
        ).fetchone()

        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    # UPDATE - devolve True se a fatura existia
    def atualizar(self, fatura):
        cursor = self.conexao.execute(
            "UPDATE Fatura SET id_ot = ?, data_emissao = ?, valor_total = ?, "
            "pago = ?, data_pagamento = ?, metodo_pagamento = ? "
            "WHERE id_fatura = ?",
            (fatura.id_ot, fatura.data_emissao, fatura.valor_total, fatura.pago,
             fatura.data_pagamento, fatura.metodo_pagamento, fatura.id_fatura)
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    # DELETE - devolve True se a fatura existia
    def eliminar(self, id_fatura):
        cursor = self.conexao.execute(
            "DELETE FROM Fatura WHERE id_fatura = ?",
            (id_fatura,)
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    # READ - faturas emitidas num mês/ano.
    # strftime é uma função do SQLite que extrai uma parte da data.
    def listar_por_mes(self, mes, ano):
        if mes < 10:
            mes_texto = "0" + str(mes)
        else:
            mes_texto = str(mes)

        linhas = self.conexao.execute(
            "SELECT * FROM Fatura WHERE strftime('%m', data_emissao) = ? "
            "AND strftime('%Y', data_emissao) = ? ORDER BY data_emissao",
            (mes_texto, str(ano))
        ).fetchall()
        return self._lista_de_objetos(linhas)

    # READ - linhas de uma OT, como dicionários, para o service calcular o valor total
    def obter_linhas_ot(self, id_ot):
        linhas = self.conexao.execute(
            "SELECT tipo, descricao, quantidade, horas_trabalhadas, preco_unitario "
            "FROM LinhaOT WHERE id_ot = ?",
            (id_ot,)
        ).fetchall()

        resultado = []
        for linha in linhas:
            resultado.append(dict(linha))
        return resultado

    # Marca a fatura como paga; devolve True se a fatura existia
    def marcar_como_paga(self, id_fatura, data_pagamento, metodo_pagamento):
        cursor = self.conexao.execute(
            "UPDATE Fatura SET pago = 1, data_pagamento = ?, metodo_pagamento = ? "
            "WHERE id_fatura = ?",
            (data_pagamento, metodo_pagamento, id_fatura)
        )
        self.conexao.commit()
        return cursor.rowcount > 0
