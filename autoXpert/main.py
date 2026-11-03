<<<<<<< HEAD
import argparse
import sqlite3
import sys
import tkinter as tk
from tkinter import ttk

from db.connection import inicializar_bd
from src.controllers.peca_controller import PecaController
from src.controllers.tecnico_controller import TecnicoController
from src.services.peca_service import PecaService
from src.services.tecnico_service import TecnicoService
from src.views.peca_view import PecaView
from src.views.tecnico_view import TecnicoView


def criar_aplicacao() -> tk.Tk:
    """Liga as camadas. Importar este modulo nao abre uma janela."""
    janela = tk.Tk()
    janela.title("AutoXpert - Tecnicos e Pecas")
    janela.geometry("1060x760")
    janela.minsize(1000, 700)
    paginas = ttk.Notebook(janela)
    paginas.pack(fill="both", expand=True)
    try:
        tecnicos = TecnicoView(paginas, TecnicoController(TecnicoService()))
        pecas = PecaView(paginas, PecaController(PecaService()))
        paginas.add(tecnicos, text="Tecnicos")
        paginas.add(pecas, text="Pecas")
    except (sqlite3.Error, tk.TclError):
        janela.destroy()
        raise
    return janela


def main() -> int:
    parser = argparse.ArgumentParser(description="Gestao de tecnicos e pecas AutoXpert.")
    parser.add_argument(
        "--inicializar-bd", action="store_true",
        help="Cria as tabelas em falta e termina sem abrir a interface.",
    )
    argumentos = parser.parse_args()
    try:
        inicializar_bd()
        if argumentos.inicializar_bd:
            print("Base de dados inicializada.")
            return 0
        janela = criar_aplicacao()
    except (sqlite3.Error, tk.TclError) as erro:
        print(f"Nao foi possivel iniciar o AutoXpert: {erro}", file=sys.stderr)
        return 1
    janela.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
=======
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
>>>>>>> main
