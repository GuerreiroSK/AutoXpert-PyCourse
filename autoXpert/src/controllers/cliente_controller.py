class ClienteController:

    def __init__(self, cliente_service):
        self.service = cliente_service

    def registar_cliente(self, nome, nif, telefone, email, morada):
        return self.service.registar(
            nome, nif, telefone, email, morada
        )

    def listar_clientes(self):
        return self.service.listar_todos()