from src.models.cliente_model import Cliente


class ClienteRepository:
    # Todo o SQL da tabela Cliente. A ligação é recebida de fora (como nos outros
    # repositórios) para os módulos partilharem a mesma e para os testes poderem
    # usar uma base de dados em memória.

    def __init__(self, conexao):
        self.conexao = conexao

    # Converte uma linha da base de dados num objeto Cliente
    def _linha_para_objeto(self, linha):
        return Cliente(
            nome=linha["nome"],
            nif=linha["NIF"],
            telefone=linha["telefone"],
            email=linha["email"],
            morada=linha["morada"],
            data_registo=linha["data_registo"],
            id_cliente=linha["id_cliente"]
        )

    # CREATE - grava o cliente e preenche o id gerado pela base de dados
    def inserir(self, cliente):
        cursor = self.conexao.execute(
            "INSERT INTO Cliente "
            "(nome, NIF, telefone, email, morada, data_registo) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cliente.nome, cliente.nif, cliente.telefone, cliente.email,
             cliente.morada, cliente.data_registo)
        )
        self.conexao.commit()
        cliente.id_cliente = cursor.lastrowid
        return cliente

    # READ - todos os clientes
    def listar_todos(self):
        linhas = self.conexao.execute(
            "SELECT * FROM Cliente ORDER BY id_cliente"
        ).fetchall()

        clientes = []
        for linha in linhas:
            clientes.append(self._linha_para_objeto(linha))
        return clientes

    # READ - um cliente (ou None se o id não existir)
    def obter_por_id(self, id_cliente):
        linha = self.conexao.execute(
            "SELECT * FROM Cliente WHERE id_cliente = ?",
            (id_cliente,)
        ).fetchone()

        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    # UPDATE - devolve True se o cliente existia
    def atualizar(self, cliente):
        cursor = self.conexao.execute(
            "UPDATE Cliente SET nome = ?, NIF = ?, telefone = ?, email = ?, "
            "morada = ?, data_registo = ? WHERE id_cliente = ?",
            (cliente.nome, cliente.nif, cliente.telefone, cliente.email,
             cliente.morada, cliente.data_registo, cliente.id_cliente)
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    # DELETE - devolve True se o cliente existia
    def eliminar(self, id_cliente):
        cursor = self.conexao.execute(
            "DELETE FROM Cliente WHERE id_cliente = ?",
            (id_cliente,)
        )
        self.conexao.commit()
        return cursor.rowcount > 0
