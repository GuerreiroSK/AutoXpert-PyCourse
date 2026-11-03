from datetime import datetime

from src.models.log_alteracao_ot_model import LogAlteracaoOT


class LogAlteracaoOTRepository:
    # Todo o SQL da tabela LogAlteracaoOT. A ligação é recebida de fora e tem de
    # devolver linhas acessíveis pelo nome da coluna (db/connection.py já o faz).

    def __init__(self, conexao):
        self.conexao = conexao

    # Converte uma linha da base de dados num objeto LogAlteracaoOT
    def _linha_para_objeto(self, linha):
        return LogAlteracaoOT(
            id_log=linha["id_log"],
            id_ot=linha["id_ot"],
            data_hora=linha["data_hora"],
            campo_alterado=linha["campo_alterado"],
            valor_anterior=linha["valor_anterior"],
            valor_novo=linha["valor_novo"]
        )

    def _lista_de_objetos(self, linhas):
        registos = []
        for linha in linhas:
            registos.append(self._linha_para_objeto(linha))
        return registos

    # Grava o registo, preenche o id e devolve-o
    def registar(self, log):
        if not log.data_hora:
            log.data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = self.conexao.execute(
            "INSERT INTO LogAlteracaoOT (id_ot, data_hora, campo_alterado, "
            "valor_anterior, valor_novo) VALUES (?, ?, ?, ?, ?)",
            (log.id_ot, log.data_hora, log.campo_alterado, log.valor_anterior,
             log.valor_novo)
        )
        self.conexao.commit()
        log.id_log = cursor.lastrowid
        return cursor.lastrowid

    def obter_por_id(self, id_log):
        linha = self.conexao.execute(
            "SELECT * FROM LogAlteracaoOT WHERE id_log = ?",
            (id_log,)
        ).fetchone()

        if linha is None:
            return None
        return self._linha_para_objeto(linha)

    # Alterações de uma OT, as mais recentes primeiro
    def listar_por_ot(self, id_ot):
        linhas = self.conexao.execute(
            "SELECT * FROM LogAlteracaoOT WHERE id_ot = ? "
            "ORDER BY data_hora DESC, id_log DESC",
            (id_ot,)
        ).fetchall()
        return self._lista_de_objetos(linhas)

    def listar_todos(self):
        linhas = self.conexao.execute(
            "SELECT * FROM LogAlteracaoOT ORDER BY data_hora DESC, id_log DESC"
        ).fetchall()
        return self._lista_de_objetos(linhas)

    # Devolve True se o registo existia
    def eliminar(self, id_log):
        cursor = self.conexao.execute(
            "DELETE FROM LogAlteracaoOT WHERE id_log = ?",
            (id_log,)
        )
        self.conexao.commit()
        return cursor.rowcount > 0
