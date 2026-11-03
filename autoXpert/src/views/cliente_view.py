import sqlite3


class ClienteView:

    def __init__(self, cliente_controller):
        self.controller = cliente_controller

    def menu(self):
        while True:
            print("\n--- Gestão de Clientes ---")
            print("1 - Registar cliente")
            print("2 - Listar clientes")
            print("0 - Voltar ao menu principal")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.adicionar_cliente()
            elif opcao == "2":
                self.listar_clientes()
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")

    def adicionar_cliente(self):
        nome = input("Nome: ")
        nif = input("NIF: ")
        telefone = input("Telefone: ")
        email = input("Email: ")
        morada = input("Morada: ")

        try:
            cliente = self.controller.registar_cliente(
                nome, nif, telefone, email, morada
            )
            print(f"\nCliente registado com sucesso! ID: {cliente.id_cliente}")

        except ValueError as erro:
            print(f"Erro: {erro}")

        except sqlite3.IntegrityError as erro:
            print(f"Erro de integridade: {erro}")

    def listar_clientes(self):
        clientes = self.controller.listar_clientes()

        if not clientes:
            print("\nNão existem clientes registados.")
            return

        print("\n--- Lista de Clientes ---")

        for cliente in clientes:
            print(
                f"ID: {cliente.id_cliente} | "
                f"Nome: {cliente.nome} | "
                f"NIF: {cliente.nif} | "
                f"Telefone: {cliente.telefone} | "
                f"Email: {cliente.email} | "
                f"Morada: {cliente.morada} | "
                f"Data de registo: {cliente.data_registo}"
            )
