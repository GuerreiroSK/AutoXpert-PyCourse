from auth import registar_utilizador

class UtilizadorRepository:
    # Todo o SQL da tabela utilizadores.

    def __init__(self, conexao):
        self.conexao = conexao

    # Lista os utilizadores sem expor as palavras-passe cifradas.
    def listar_todos(self):
        cursor = self.conexao.execute(
            """
            SELECT id, login, perfil
            FROM utilizadores
            ORDER BY login COLLATE NOCASE
            """
        )
        return [dict(linha) for linha in cursor.fetchall()]

    # Devolve um utilizador pelo ID ou None se não existir.
    def obter_por_id(self, id_utilizador):
        linha = self.conexao.execute(
            """
            SELECT id, login, perfil
            FROM utilizadores
            WHERE id = ?
            """,
            (id_utilizador,)
        ).fetchone()

        if linha is None:
            return None

        return dict(linha)

    # Conta quantos administradores existem.
    def contar_administradores(self):
        linha = self.conexao.execute(
            """
            SELECT COUNT(*) AS total
            FROM utilizadores
            WHERE perfil = 'administrador'
            """
        ).fetchone()

        return linha["total"]

    # Regista um utilizador, reutilizando a autenticação existente.
    def registar(self, login, senha, perfil):
        registar_utilizador(
            self.conexao,
            login,
            senha,
            perfil
        )

    # Elimina um utilizador pelo ID.
    def eliminar(self, id_utilizador):
        cursor = self.conexao.execute(
            "DELETE FROM utilizadores WHERE id = ?",
            (id_utilizador,)
        )
        self.conexao.commit()

        return cursor.rowcount > 0
