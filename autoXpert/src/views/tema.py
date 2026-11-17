from tkinter import font, ttk


COR_FUNDO = "#f2f4f7"
COR_CABECALHO = "#1A3A5C"
COR_TEXTO_CABECALHO = "#ffffff"
COR_ATIVA = "#2d527f"
COR_DESATIVADA = "#667085"
COR_BORDA = "#cbd2dc"
COR_PERIGO = "#c24848"
COR_PERIGO_ATIVA = "#a63c3c"
COR_LINHA_PAR = "#ffffff"
COR_LINHA_IMPAR = "#e8edf4"


def configurar_linhas_alternadas(tabela):
    tabela.tag_configure("linha_par", background=COR_LINHA_PAR)
    tabela.tag_configure("linha_impar", background=COR_LINHA_IMPAR)


def tags_linha_alternada(tabela, tags=()):
    if len(tabela.get_children()) % 2 == 0:
        faixa = "linha_par"
    else:
        faixa = "linha_impar"
    return (faixa,) + tuple(tags)


def aplicar_tema(root):
    """Aplica cores, fontes e estilos comuns antes de construir as vistas."""
    estilo = ttk.Style(root)
    estilo.theme_use("clam")
    fonte = font.nametofont("TkDefaultFont", root=root)
    fonte.configure(size=10)
    familia = fonte.actual("family")

    root.configure(background=COR_FUNDO)
    root.option_add("*Toplevel.background", COR_FUNDO)
    root.option_add("*Font", "TkDefaultFont")
    root.option_add("*TCombobox*Listbox.background", COR_TEXTO_CABECALHO)
    root.option_add("*TCombobox*Listbox.foreground", COR_CABECALHO)
    root.option_add("*TCombobox*Listbox.selectBackground", COR_CABECALHO)
    root.option_add("*TCombobox*Listbox.selectForeground", COR_TEXTO_CABECALHO)

    estilo.configure(
        ".", background=COR_FUNDO, foreground=COR_CABECALHO,
        font="TkDefaultFont"
    )
    estilo.map(".", foreground=[("disabled", COR_DESATIVADA)])
    estilo.configure("TFrame", background=COR_FUNDO)
    estilo.configure("TLabel", background=COR_FUNDO)
    estilo.configure("TLabelframe", background=COR_FUNDO, bordercolor=COR_BORDA)
    estilo.configure(
        "TLabelframe.Label", background=COR_FUNDO, font=(familia, 10, "bold")
    )
    estilo.configure(
        "Cabecalho.TLabel", background=COR_CABECALHO,
        foreground=COR_TEXTO_CABECALHO, padding=(15, 10),
        font=(familia, 14, "bold")
    )
    estilo.configure("Destaque.TLabel", font=(familia, 12, "bold"))
    estilo.configure("Rotulo.TLabel", font=(familia, 10, "bold"))
    estilo.map(
        "TCheckbutton", background=[("active", COR_FUNDO)],
        foreground=[("disabled", COR_DESATIVADA), ("active", COR_CABECALHO)]
    )
    estilo.configure(
        "TButton", background=COR_CABECALHO, foreground=COR_TEXTO_CABECALHO,
        font=("Calibri", 10, "bold"), padding=(10, 5), borderwidth=1
    )
    estilo.configure("Menu.TButton", padding=(10, 10))
    estilo.map(
        "TButton",
        background=[("disabled", COR_FUNDO), ("pressed", COR_CABECALHO),
                    ("active", COR_ATIVA)],
        foreground=[("disabled", COR_DESATIVADA),
                    ("!disabled", COR_TEXTO_CABECALHO)],
    )
    estilo.configure("Perigo.TButton", background=COR_PERIGO)
    estilo.map(
        "Perigo.TButton",
        background=[("disabled", COR_FUNDO), ("pressed", COR_PERIGO_ATIVA),
                    ("active", COR_PERIGO_ATIVA)]
    )
    estilo.configure("Menu.Perigo.TButton", padding=(10, 10))
    estilo.configure(
        "TEntry", fieldbackground=COR_TEXTO_CABECALHO,
        foreground=COR_CABECALHO, bordercolor=COR_BORDA
    )
    estilo.map(
        "TEntry", fieldbackground=[("disabled", COR_FUNDO)],
        foreground=[("disabled", COR_DESATIVADA)]
    )
    estilo.configure(
        "TCombobox", fieldbackground=COR_TEXTO_CABECALHO,
        foreground=COR_CABECALHO, bordercolor=COR_BORDA,
        arrowsize=14
    )
    estilo.map(
        "TCombobox",
        fieldbackground=[("disabled", COR_FUNDO),
                         ("readonly", COR_TEXTO_CABECALHO)],
        foreground=[("disabled", COR_DESATIVADA), ("readonly", COR_CABECALHO)],
    )
    estilo.configure(
        "Treeview", background=COR_TEXTO_CABECALHO,
        fieldbackground=COR_TEXTO_CABECALHO, foreground=COR_CABECALHO,
        rowheight=26, bordercolor=COR_BORDA
    )
    estilo.map(
        "Treeview",
        background=[("selected", COR_CABECALHO)],
        foreground=[("selected", COR_TEXTO_CABECALHO)],
    )
    estilo.configure(
        "Treeview.Heading", background=COR_CABECALHO,
        foreground=COR_TEXTO_CABECALHO, font=(familia, 10, "bold"),
        padding=(6, 5)
    )
    estilo.map("Treeview.Heading", background=[("active", COR_ATIVA)])
