import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Aspeto comum a todas as janelas do AutoXpert.
# Cada view usa estas funções em vez de montar o seu próprio aspeto, para a
# aplicação ficar igual em todos os módulos (cabeçalho, tabelas, formulários, avisos).

COR_FUNDO = "#f2f4f7"
COR_CABECALHO = "#1f3a5f"
COR_TEXTO_CABECALHO = "#ffffff"


# Chamar uma vez, logo a seguir a criar a janela principal (tk.Tk())
def aplicar_estilo(raiz):
    estilo = ttk.Style(raiz)
    if "clam" in estilo.theme_names():
        estilo.theme_use("clam")
    raiz.configure(background=COR_FUNDO)

    estilo.configure(".", background=COR_FUNDO)
    estilo.configure("TButton", padding=(10, 5))
    estilo.configure("Menu.TButton", padding=(10, 10), font=("TkDefaultFont", 12))
    estilo.configure("Cabecalho.TLabel", background=COR_CABECALHO,
                     foreground=COR_TEXTO_CABECALHO, padding=(15, 10),
                     font=("TkDefaultFont", 16, "bold"))
    estilo.configure("Treeview", rowheight=24)
    estilo.configure("Treeview.Heading", font=("TkDefaultFont", 10, "bold"))


# ================= Janelas e blocos comuns =================

# Cria uma janela nova, um pouco deslocada em relação à janela de onde foi aberta
def criar_janela(pai, titulo, largura, altura):
    janela = tk.Toplevel(pai)
    janela.title(titulo)
    janela.configure(background=COR_FUNDO)
    x = pai.winfo_rootx() + 60
    y = pai.winfo_rooty() + 40
    janela.geometry(str(largura) + "x" + str(altura) + "+" + str(x) + "+" + str(y))
    return janela


# Faixa azul com o título do módulo, no topo de cada janela
def criar_cabecalho(janela, titulo):
    cabecalho = ttk.Label(janela, text=titulo, style="Cabecalho.TLabel", anchor="w")
    cabecalho.pack(fill="x")
    return cabecalho


# Barra no fundo da janela para mensagens curtas. Devolve a variável de texto:
#   barra = criar_barra_estado(janela);  barra.set("3 registos")
def criar_barra_estado(janela):
    texto = tk.StringVar()
    ttk.Label(janela, textvariable=texto, relief="sunken", anchor="w").pack(
        fill="x", side="bottom")
    return texto


# Tabela com barra de deslocamento. colunas é uma lista de
# (nome, título, largura, alinhamento), ex.: ("id", "ID", 50, "center")
def criar_tabela(pai, colunas, altura):
    quadro = ttk.Frame(pai)
    quadro.pack(fill="both", expand=True)

    nomes = []
    for coluna in colunas:
        nomes.append(coluna[0])

    tabela = ttk.Treeview(quadro, columns=nomes, show="headings",
                          height=altura, selectmode="browse")
    for nome, titulo, largura, alinhamento in colunas:
        tabela.heading(nome, text=titulo)
        tabela.column(nome, width=largura, anchor=alinhamento)

    barra = ttk.Scrollbar(quadro, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=barra.set)
    tabela.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return tabela


def limpar_tabela(tabela):
    for item in tabela.get_children():
        tabela.delete(item)


# None aparece como texto vazio
def texto(valor):
    if valor is None:
        return ""
    return valor


# ================= Avisos =================

def mostrar_erro(pai, titulo, mensagem):
    messagebox.showerror(titulo, mensagem, parent=pai)


def mostrar_info(pai, titulo, mensagem):
    messagebox.showinfo(titulo, mensagem, parent=pai)


def perguntar_sim_nao(pai, titulo, mensagem):
    return messagebox.askyesno(titulo, mensagem, parent=pai)


# Traduz erros da base de dados para uma frase que o utilizador perceba
def texto_do_erro(erro):
    mensagem = str(erro)
    if isinstance(erro, sqlite3.IntegrityError):
        if "UNIQUE" in mensagem:
            return "Já existe um registo com esse valor (valor repetido)."
        if "FOREIGN KEY" in mensagem:
            return ("Operação impedida: o registo está ligado a outros registos "
                    "(ou refere um que não existe).")
    return mensagem


# ================= Janelas só para mostrar dados =================

# Abre uma janela com uma tabela (usada para listas e históricos).
# linhas é uma lista de tuplos, com um valor por coluna.
def mostrar_tabela(pai, titulo, colunas, linhas, largura, altura):
    janela = criar_janela(pai, titulo, largura, altura)
    criar_cabecalho(janela, titulo)

    corpo = ttk.Frame(janela, padding=10)
    corpo.pack(fill="both", expand=True)
    tabela = criar_tabela(corpo, colunas, 12)
    for linha in linhas:
        tabela.insert("", "end", values=linha)

    ttk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=(0, 10))
    return janela


# Abre uma janela com pares "rótulo: valor" (usada para os dados de um registo).
# pares é uma lista de (rótulo, valor).
def mostrar_detalhe(pai, titulo, pares):
    janela = criar_janela(pai, titulo, 420, 80 + 30 * len(pares) + 60)
    criar_cabecalho(janela, titulo)

    corpo = ttk.Frame(janela, padding=15)
    corpo.pack(fill="both", expand=True)
    linha = 0
    for rotulo, valor in pares:
        ttk.Label(corpo, text=rotulo + ":", font=("TkDefaultFont", 10, "bold")).grid(
            row=linha, column=0, sticky="ne", padx=(0, 10), pady=3)
        ttk.Label(corpo, text=str(texto(valor)), wraplength=250, justify="left").grid(
            row=linha, column=1, sticky="nw", pady=3)
        linha += 1

    ttk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=(0, 10))
    return janela


# ================= Formulários =================

class DialogoFormulario:
    # Janela com campos para preencher, que bloqueia a janela de trás até ser
    # fechada. Devolve um dicionário {chave: texto} ou None se for cancelada.
    #
    # campos: lista de (chave, rótulo) para uma caixa de texto, ou
    #         (chave, rótulo, opções) para uma lista de escolha (sem escrita livre)
    # valores: dicionário com os valores iniciais (opcional)
    # validar: função opcional que recebe o dicionário e devolve uma mensagem de
    #          erro (a janela fica aberta) ou None (tudo certo)

    def __init__(self, pai, titulo, campos, valores=None, texto_botao="Guardar",
                 validar=None):
        self.pai = pai
        self.validar = validar
        self.resultado = None
        self.entradas = {}

        self.janela = tk.Toplevel(pai)
        self.janela.title(titulo)
        self.janela.configure(background=COR_FUNDO)
        self.janela.transient(pai)
        self.janela.resizable(False, False)

        corpo = ttk.Frame(self.janela, padding=15)
        corpo.pack()

        linha = 0
        for campo in campos:
            chave = campo[0]
            rotulo = campo[1]
            ttk.Label(corpo, text=rotulo + ":").grid(
                row=linha, column=0, sticky="e", padx=(0, 8), pady=5)
            if len(campo) > 2:
                entrada = ttk.Combobox(corpo, values=campo[2], state="readonly", width=28)
                entrada.set(campo[2][0])
            else:
                entrada = ttk.Entry(corpo, width=32)
            entrada.grid(row=linha, column=1, sticky="w", pady=5)
            self.entradas[chave] = entrada
            linha += 1

        if valores is not None:
            for chave in valores:
                self.escrever(self.entradas[chave], valores[chave])

        botoes = ttk.Frame(corpo)
        botoes.grid(row=linha, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(botoes, text=texto_botao, command=self.guardar).pack(side="left", padx=6)
        ttk.Button(botoes, text="Cancelar", command=self.cancelar).pack(side="left", padx=6)

        self.janela.bind("<Return>", self.ao_carregar_enter)
        self.janela.bind("<Escape>", self.ao_carregar_escape)

        # Abre por cima da janela de trás (em vez de no canto do ecrã)
        x = pai.winfo_rootx() + 120
        y = pai.winfo_rooty() + 80
        self.janela.geometry("+" + str(x) + "+" + str(y))

        self.janela.wait_visibility()  # no Linux, o grab só funciona com a janela já visível
        self.janela.grab_set()
        primeira = self.entradas[campos[0][0]]
        primeira.focus_set()

    def escrever(self, entrada, valor):
        if valor is None:
            valor = ""
        if isinstance(entrada, ttk.Combobox):
            entrada.set(str(valor))
        else:
            entrada.delete(0, "end")
            entrada.insert(0, str(valor))

    def guardar(self):
        dados = {}
        for chave in self.entradas:
            dados[chave] = self.entradas[chave].get().strip()
        if self.validar is not None:
            erro = self.validar(dados)
            if erro is not None:
                messagebox.showerror("Erro", erro, parent=self.janela)
                return
        self.resultado = dados
        self.janela.destroy()

    def cancelar(self):
        self.janela.destroy()

    def ao_carregar_enter(self, evento):
        self.guardar()

    def ao_carregar_escape(self, evento):
        self.cancelar()

    # Espera que a janela seja fechada e devolve o que o utilizador preencheu
    def mostrar(self):
        self.pai.wait_window(self.janela)
        return self.resultado


# Atalho: abre o formulário e devolve o dicionário (ou None se cancelado)
def pedir_dados(pai, titulo, campos, valores=None, texto_botao="Guardar", validar=None):
    return DialogoFormulario(pai, titulo, campos, valores, texto_botao, validar).mostrar()


def _validar_texto_obrigatorio(dados):
    if dados["valor"] == "":
        return "Este campo é obrigatório"
    return None


# Pede um único texto (obrigatório por defeito). Devolve o texto ou None se cancelado.
def pedir_texto(pai, titulo, rotulo, valor_inicial="", obrigatorio=True):
    validar = None
    if obrigatorio:
        validar = _validar_texto_obrigatorio
    dados = pedir_dados(pai, titulo, [("valor", rotulo)], {"valor": valor_inicial},
                        "OK", validar)
    if dados is None:
        return None
    return dados["valor"]


def _validar_inteiro_positivo(dados):
    try:
        numero = int(dados["valor"])
    except ValueError:
        return "Tem de indicar um número inteiro"
    if numero < 1:
        return "O número tem de ser maior que zero"
    return None


# Pede um número inteiro (>= 1), sem deixar fechar enquanto não for válido.
# Devolve o número ou None se cancelado.
def pedir_inteiro(pai, titulo, rotulo):
    dados = pedir_dados(pai, titulo, [("valor", rotulo)], None, "OK",
                        _validar_inteiro_positivo)
    if dados is None:
        return None
    return int(dados["valor"])
