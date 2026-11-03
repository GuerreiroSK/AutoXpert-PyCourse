class ClienteController:

    def __init__(self, cliente_service):
        self.service = cliente_service

    # CREATE - Registar cliente
    def registar_cliente(self, nome, nif, telefone, email, morada):
        return self.service.registar(
            nome, nif, telefone, email, morada
        )

    # READ - Listar todos os clientes
    def listar_clientes(self):
        return self.service.listar_todos()

    # READ - Consultar cliente por ID
    def consultar_cliente(self, id_cliente):
        return self.service.obter_por_id(id_cliente)

    # UPDATE - Atualizar cliente
    def atualizar_cliente(self, cliente):
        return self.service.atualizar(cliente)

    # DELETE - Eliminar cliente
    def eliminar_cliente(self, id_cliente):
        return self.service.eliminar(id_cliente)