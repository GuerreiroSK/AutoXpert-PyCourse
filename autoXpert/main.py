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