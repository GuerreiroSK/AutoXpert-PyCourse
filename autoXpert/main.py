from db.connection import inicializar_bd

from src.repositories.cliente_repository import ClienteRepository
from src.services.cliente_service import ClienteService
from src.controllers.cliente_controller import ClienteController
from src.views.cliente_view import ClienteView
from src.repositories.fatura_repository import FaturaRepository
from src.services.fatura_service import FaturaService
from src.controllers.fatura_controller import FaturaController
from src.views.fatura_view import FaturaView


def main():
    inicializar_bd()

    # Inicializar o módulo de clientes
    cliente_repository = ClienteRepository()
    cliente_service = ClienteService(cliente_repository)
    cliente_controller = ClienteController(cliente_service)
    cliente_view = ClienteView(cliente_controller)

    # Inicializar o módulo de faturacao

    fatura_repository = FaturaRepository()
    fatura_service = FaturaService(fatura_repository)
    fatura_controller = FaturaController(fatura_service)
    fatura_view = FaturaView(fatura_controller)

    # Menu principal
    while True:
        print("\n===== AutoXpert =====")
        print("1 - Gestão de clientes")
        print("2 - Gestão de viaturas")
        print("3 - Gestão de técnicos")
        print("4 - Gestão de peças")
        print("5 - Ordens de trabalho")
        print("6 - Faturação")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cliente_view.menu()
        elif opcao == "6":
            fatura_view.menu()
        elif opcao == "0":
            print("A sair do AutoXpert...")
            break
        elif opcao in ("2", "3", "4", "5"):
            print("Este módulo ainda não está implementado.")
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()