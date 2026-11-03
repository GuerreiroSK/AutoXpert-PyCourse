from src.models.linha_ot_model import LinhaOT


class LinhaOTRepository:
    COLUNAS = ("id_linha, id_ot, tipo, descricao, quantidade, "
               "horas_trabalhadas, preco_unitario, id_peca")
    BASE_SELECT = "SELECT " + COLUNAS + " FROM LinhaOT"

    def __init__(self, conexao):
        self.conexao = conexao

    # Converte uma linha da base de dados (tuplo) num objeto LinhaOT
    def _linha_para_objeto(self, linha):
        return LinhaOT(
            id_linha=linha[0],
            id_ot=linha[1],
            tipo=linha[2],
            descricao=linha[3],
            quantidade=linha[4],
            horas_trabalhadas=linha[5],
            preco_unitario=linha[6],
            id_peca=linha[7],
        )

    # Executa um SELECT e devolve uma lista de objetos LinhaOT
    def _listar_com_sql(self, sql, parametros):
        cursor = self.conexao.cursor()
        cursor.execute(sql, tuple(parametros))
        resultado = []
        for linha in cursor.fetchall():
            resultado.append(self._linha_para_objeto(linha))
        return resultado

    # RF04: grava uma nova linha e preenche o id gerado pela base de dados
    def inserir(self, linha_ot):
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO LinhaOT (id_ot, tipo, descricao, quantidade, "
            "horas_trabalhadas, preco_unitario, id_peca) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (linha_ot.id_ot, linha_ot.tipo, linha_ot.descricao,
             linha_ot.quantidade, linha_ot.horas_trabalhadas,
             linha_ot.preco_unitario, linha_ot.id_peca),
        )
        self.conexao.commit()
        linha_ot.id_linha = cursor.lastrowid
        return linha_ot

    def listar(self):
        return self._listar_com_sql(self.BASE_SELECT + " ORDER BY id_linha", [])

    # Linhas de uma OT (usado para mostrar o detalhe e para calcular o custo, RF13)
    def listar_por_ot(self, id_ot):
        return self._listar_com_sql(
            self.BASE_SELECT + " WHERE id_ot = ? ORDER BY id_linha", [id_ot])

    # RNF03: em que OTs foi usada uma determinada peça
    def listar_por_peca(self, id_peca):
        return self._listar_com_sql(
            self.BASE_SELECT + " WHERE id_peca = ? ORDER BY id_ot, id_linha",
            [id_peca])

    # Devolve a linha ou None se o id não existir
    def procurar_por_id(self, id_linha):
        lista = self._listar_com_sql(
            self.BASE_SELECT + " WHERE id_linha = ?", [id_linha])
        if len(lista) == 0:
            return None
        return lista[0]

    # Atualiza todos os campos da linha; devolve True se a linha existia
    def atualizar(self, linha_ot):
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE LinhaOT SET id_ot = ?, tipo = ?, descricao = ?, "
            "quantidade = ?, horas_trabalhadas = ?, preco_unitario = ?, "
            "id_peca = ? WHERE id_linha = ?",
            (linha_ot.id_ot, linha_ot.tipo, linha_ot.descricao,
             linha_ot.quantidade, linha_ot.horas_trabalhadas,
             linha_ot.preco_unitario, linha_ot.id_peca, linha_ot.id_linha),
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    def apagar(self, id_linha):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM LinhaOT WHERE id_linha = ?", (id_linha,))
        self.conexao.commit()
        return cursor.rowcount > 0

    # Apaga todas as linhas de uma OT (fazer antes de apagar a própria OT).
    # Devolve quantas linhas foram apagadas.
    def apagar_por_ot(self, id_ot):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM LinhaOT WHERE id_ot = ?", (id_ot,))
        self.conexao.commit()
        return cursor.rowcount