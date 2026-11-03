from src.models.tecnico_model import Tecnico


class TecnicoRepository:
    # Todo o SQL da tabela Tecnico. A ligação é recebida de fora (como nos outros
    # repositórios) e tem de devolver linhas acessíveis pelo nome da coluna.

    def __init__(self, conexao):
        self.conexao = conexao

    # Converte uma linha da base de dados num objeto Tecnico
    def _linha_para_objeto(self, linha):
        return Tecnico(
            nome=linha["nome"],
            especialidade=linha["especialidade"],
            custo_hora=linha["custo_hora"],
            ativo=bool(linha["ativo"]),
            id_tecnico=linha["id_tecnico"]
        )

    # Grava o técnico e preenche o id gerado pela base de dados
    def inserir(self, tecnico):
        cursor = self.conexao.execute(
            "INSERT INTO Tecnico (nome, especialidade, custo_hora, ativo) "
            "VALUES (?, ?, ?, ?)",
            (tecnico.nome, tecnico.especialidade, tecnico.custo_hora,
             int(tecnico.ativo))
        )
        self.conexao.commit()
        tecnico.id_tecnico = cursor.lastrowid
        return tecnico

    # Todos os técnicos (ou só os ativos), por ordem alfabética
    def listar_todos(self, apenas_ativos=False):
        sql = "SELECT * FROM Tecnico"
        if apenas_ativos:
            sql += " WHERE ativo = 1"
        sql += " ORDER BY nome, id_tecnico"

        tecnicos = []
        for linha in self.conexao.execute(sql).fetchall():
            tecnicos.append(self._linha_para_objeto(linha))
        return tecnicos

    # Devolve o técnico ou None se o id não existir
    def obter_por_id(self, id_tecnico):
        linha = self.conexao.execute(
            "SELECT * FROM Tecnico WHERE id_tecnico = ?",
            (id_tecnico,)
        ).fetchone()

        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    # Devolve True se o técnico existia
    def atualizar(self, tecnico):
        cursor = self.conexao.execute(
            "UPDATE Tecnico SET nome = ?, especialidade = ?, custo_hora = ?, "
            "ativo = ? WHERE id_tecnico = ?",
            (tecnico.nome, tecnico.especialidade, tecnico.custo_hora,
             int(tecnico.ativo), tecnico.id_tecnico)
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    # Devolve True se o técnico existia
    def eliminar(self, id_tecnico):
        cursor = self.conexao.execute(
            "DELETE FROM Tecnico WHERE id_tecnico = ?",
            (id_tecnico,)
        )
        self.conexao.commit()
        return cursor.rowcount > 0
