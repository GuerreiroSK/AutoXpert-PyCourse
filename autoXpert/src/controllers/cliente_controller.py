from src.rbac import require_perfil


class ClienteController:

    def __init__(self, cliente_service, token=None):
        self.service = cliente_service
        self.token = token

    # CREATE - Registar cliente
    @require_perfil("administrador", "rececionista")
    def registar_cliente(self, nome, nif, telefone, email, morada):
        return self.service.registar(
            nome, nif, telefone, email, morada
        )

    # READ - Listar todos os clientes
    @require_perfil("administrador", "rececionista")
    def listar_clientes(self):
        return self.service.listar_todos()

    # READ - Consultar cliente por ID
    @require_perfil("administrador", "rececionista")
    def consultar_cliente(self, id_cliente):
        return self.service.obter_por_id(id_cliente)

    # UPDATE - Atualizar cliente
    @require_perfil("administrador", "rececionista")
    def atualizar_cliente(self, cliente):
        return self.service.atualizar(cliente)

    # DELETE - Eliminar cliente
    @require_perfil("administrador", "rececionista")
    def eliminar_cliente(self, id_cliente):
        return self.service.eliminar(id_cliente)
