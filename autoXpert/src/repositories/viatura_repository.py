from src.models.viatura_model import Viatura


class ViaturaRepository:
    # Todo o SQL da tabela Viatura. A ligação é recebida de fora e tem de devolver
    # linhas acessíveis pelo nome da coluna (db/connection.py já o faz).

    def __init__(self, conexao):
        self.conexao = conexao

    # Converte uma linha da base de dados num objeto Viatura
    def _linha_para_objeto(self, linha):
        return Viatura(
            id_viatura=linha["id_viatura"],
            matricula=linha["matricula"],
            marca=linha["marca"],
            modelo=linha["modelo"],
            ano=linha["ano"],
            cor=linha["cor"],
            km_estrada=linha["km_estrada"],
            id_cliente=linha["id_cliente"]
        )

    def _lista_de_objetos(self, linhas):
        viaturas = []
        for linha in linhas:
            viaturas.append(self._linha_para_objeto(linha))
        return viaturas

    # Grava a viatura, preenche o id e devolve-o
    def criar(self, viatura):
        cursor = self.conexao.execute(
            "INSERT INTO Viatura (matricula, marca, modelo, ano, cor, "
            "km_estrada, id_cliente) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (viatura.matricula, viatura.marca, viatura.modelo, viatura.ano,
             viatura.cor, viatura.km_estrada, viatura.id_cliente)
        )
        self.conexao.commit()
        viatura.id_viatura = cursor.lastrowid
        return cursor.lastrowid

    def obter_por_id(self, id_viatura):
        linha = self.conexao.execute(
            "SELECT * FROM Viatura WHERE id_viatura = ?",
            (id_viatura,)
        ).fetchone()

        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    def obter_por_matricula(self, matricula):
        linha = self.conexao.execute(
            "SELECT * FROM Viatura WHERE matricula = ?",
            (matricula,)
        ).fetchone()

        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    def listar_todas(self):
        linhas = self.conexao.execute(
            "SELECT * FROM Viatura ORDER BY id_viatura"
        ).fetchall()
        return self._lista_de_objetos(linhas)

    def listar_por_cliente(self, id_cliente):
        linhas = self.conexao.execute(
            "SELECT * FROM Viatura WHERE id_cliente = ? ORDER BY id_viatura",
            (id_cliente,)
        ).fetchall()
        return self._lista_de_objetos(linhas)

    # Devolve True se a viatura existia
    def atualizar(self, viatura):
        if viatura.id_viatura is None:
            return False

        cursor = self.conexao.execute(
            "UPDATE Viatura SET matricula = ?, marca = ?, modelo = ?, ano = ?, "
            "cor = ?, km_estrada = ?, id_cliente = ? WHERE id_viatura = ?",
            (viatura.matricula, viatura.marca, viatura.modelo, viatura.ano,
             viatura.cor, viatura.km_estrada, viatura.id_cliente,
             viatura.id_viatura)
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    # Devolve True se a viatura existia
    def eliminar(self, id_viatura):
        cursor = self.conexao.execute(
            "DELETE FROM Viatura WHERE id_viatura = ?",
            (id_viatura,)
        )
        self.conexao.commit()
        return cursor.rowcount > 0
