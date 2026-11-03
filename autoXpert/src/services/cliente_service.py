from datetime import date
from src.models.cliente_model import Cliente


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

    # READ - Consultar cliente por ID
    def obter_por_id(self, id_cliente):
        cliente = self.repository.obter_por_id(id_cliente)

        if cliente is None:
            raise ValueError("Cliente não encontrado.")

        return cliente

    # UPDATE - Atualizar cliente
    def atualizar(self, cliente):
        if not cliente.nome or not cliente.nome.strip():
            raise ValueError("O nome é obrigatório.")

        if cliente.telefone and len(cliente.telefone) > 20:
            raise ValueError("O telefone não pode ultrapassar 20 caracteres.")

        if self.repository.obter_por_id(cliente.id_cliente) is None:
            raise ValueError("Cliente não encontrado.")

        cliente.nome = cliente.nome.strip() #eliminar possiveis espaços em branco

        return self.repository.atualizar(cliente)

    # DELETE - Eliminar cliente
    def eliminar(self, id_cliente):
        if self.repository.obter_por_id(id_cliente) is None:
            raise ValueError("Cliente não encontrado.")

        return self.repository.eliminar(id_cliente)