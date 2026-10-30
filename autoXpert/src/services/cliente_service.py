from datetime import date
from src.models.cliente_models import Cliente


class ClienteService:

    def __init__(self, cliente_repository):
        self.repository = cliente_repository

    def registar(self, nome, nif, telefone, email, morada):
        if not nome or not nome.strip():
            raise ValueError("O nome é obrigatório.")

        if telefone and len(telefone) > 20:
            raise ValueError("O telefone não pode exceder 20 caracteres.")

        cliente = Cliente(
            nome=nome.strip(),
            nif=nif or None,
            telefone=telefone or None,
            email=email or None,
            morada=morada or None,
            data_registo=date.today().isoformat()
        )

        return self.repository.inserir(cliente)

    def listar_todos(self):
        return self.repository.listar_todos()