
from auth import PERFIS


class UtilizadorService:
    # Regras de negócio da gestão de utilizadores.

    def __init__(self, utilizador_repository):
        self.repository = utilizador_repository

    def listar(self):
        return self.repository.listar_todos()

    def criar(self, login, senha, confirmacao, perfil):
        login = (login or "").strip()

        if not login:
            raise ValueError("O nome de utilizador é obrigatório.")

        if not senha:
            raise ValueError("A palavra-passe é obrigatória.")

        if senha != confirmacao:
            raise ValueError("As palavras-passe não coincidem.")

        if perfil not in PERFIS:
            raise ValueError("Perfil inválido.")

        self.repository.registar(login, senha, perfil)

    def eliminar(self, id_utilizador, login_sessao):
        utilizador = self.repository.obter_por_id(id_utilizador)

        if utilizador is None:
            raise ValueError("O utilizador selecionado já não existe.")

        # Impede que o administrador elimine a própria conta.
        if utilizador["login"].casefold() == login_sessao.casefold():
            raise ValueError("Não pode eliminar a conta que está a utilizar.")

        # Impede a eliminação do último administrador.
        if (
            utilizador["perfil"] == "administrador"
            and self.repository.contar_administradores() <= 1
        ):
            raise ValueError("Não pode eliminar o último administrador.")

        if not self.repository.eliminar(id_utilizador):
            raise ValueError("Não foi possível eliminar o utilizador.")
