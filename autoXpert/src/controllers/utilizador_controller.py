from auth import validar_token
from src.rbac import require_perfil


class UtilizadorController:

    def __init__(self, servico, token=None):
        self.servico = servico
        self.token = token

    # Lista os utilizadores.
    @require_perfil("administrador")
    def listar(self):
        return self.servico.listar()

    # Cria uma nova conta.
    @require_perfil("administrador")
    def criar(self, login, senha, confirmacao, perfil):
        return self.servico.criar(
            login,
            senha,
            confirmacao,
            perfil
        )

    # Elimina uma conta, impedindo a eliminação da sessão atual.
    @require_perfil("administrador")
    def eliminar(self, id_utilizador):
        payload = validar_token(self.token)

        return self.servico.eliminar(
            id_utilizador,
            payload["sub"]
        )