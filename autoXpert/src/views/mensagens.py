from collections.abc import Callable
import sqlite3
import tkinter as tk
from tkinter import messagebox


def executar_acao(janela: tk.Misc, acao: Callable[[], None]) -> None:
    """Mostra erros esperados sem apagar os dados introduzidos no formulario."""
    try:
        acao()
    except ValueError as erro:
        messagebox.showwarning("Verifique os dados", str(erro), parent=janela)
    except sqlite3.IntegrityError as erro:
        messagebox.showerror(
            "Registo nao permitido",
            "Verifique referencias repetidas, valores negativos ou ligacoes "
            f"a ordens de trabalho.\n\nDetalhe: {erro}",
            parent=janela,
        )
    except sqlite3.Error as erro:
        messagebox.showerror("Erro na base de dados", str(erro), parent=janela)
