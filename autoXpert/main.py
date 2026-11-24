import tkinter as tk
from tkinter import messagebox

from auth import autenticar, criar_token, registar_utilizador, validar_token

from db.connection import inicializar_bd, get_connection

from src.repositories.cliente_repository import ClienteRepository
from src.services.cliente_service import ClienteService
from src.controllers.cliente_controller import ClienteController
from src.views.cliente_view import ClienteView

from src.repositories.viatura_repository import ViaturaRepository
from src.services.viatura_service import ViaturaService
from src.controllers.viatura_controller import ViaturaController
from src.views.viatura_view import ViaturaView

from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.repositories.linha_ot_repository import LinhaOTRepository
from src.services.ot_service import OrdemTrabalhoService
from src.services.linha_ot_service import LinhaOTService
from src.controllers.ot_controller import OrdemTrabalhoController
from src.controllers.linha_ot_controller import LinhaOTController
from src.views.ot_view import JanelaOTs

from src.repositories.fatura_repository import FaturaRepository
from src.services.fatura_service import FaturaService
from src.controllers.fatura_controller import FaturaController
from src.views.fatura_view import FaturaView

from src.repositories.log_alteracao_ot_repository import LogAlteracaoOTRepository
from src.services.log_alteracao_ot_service import LogAlteracaoOTService
from src.controllers.log_alteracao_ot_controller import LogAlteracaoOTController
from src.views.log_alteracao_ot_view import LogAlteracaoOTView

from src.repositories.tecnico_repository import TecnicoRepository
from src.services.tecnico_service import TecnicoService
from src.controllers.tecnico_controller import TecnicoController
from src.views.tecnico_view import TecnicoView

from src.repositories.utilizador_repository import UtilizadorRepository
from src.services.utilizador_service import UtilizadorService
from src.controllers.utilizador_controller import UtilizadorController
from src.views.utilizador_view import UtilizadorView

from src.repositories.peca_repository import PecaRepository
from src.services.peca_service import PecaService
from src.controllers.peca_controller import PecaController
from src.views.peca_view import PecaView

from src.views.estilo import criar_janela, criar_cabecalho
from src.views.menu_principal_view import MenuPrincipalView
from src.views.tema import aplicar_tema
from src.views.autenticacao_view import AutenticacaoView


class AplicacaoAutoXpert:
    # Liga todas as camadas (repositório -> service -> controller -> view) de cada
    # módulo e entrega ao menu principal a função que abre cada um.
    # Todos os repositórios partilham a mesma ligação à base de dados.

    def __init__(self, raiz, token):
        self.raiz = raiz
        # O JWT representa a sessão autenticada durante a utilização da aplicação.
        self.token = token
        self.utilizador = validar_token(token)
        self.janela_ots = None
        self.janela_tecnicos = None
        self.janela_pecas = None
        self.janela_utilizadores = None

        self.conexao = get_connection()

        # Repositórios (só eles têm SQL)
        cliente_repo = ClienteRepository(self.conexao)
        viatura_repo = ViaturaRepository(self.conexao)
        tecnico_repo = TecnicoRepository(self.conexao)
        peca_repo = PecaRepository(self.conexao)
        ot_repo = OrdemTrabalhoRepository(self.conexao)
        linha_repo = LinhaOTRepository(self.conexao)
        fatura_repo = FaturaRepository(self.conexao)
        log_repo = LogAlteracaoOTRepository(self.conexao)
        utilizador_repo = UtilizadorRepository(self.conexao)

        # Clientes
        self.cliente_controller = ClienteController(ClienteService(cliente_repo), token)
        self.cliente_view = ClienteView(raiz, self.cliente_controller)

        # Viaturas (o formulário mostra a lista de clientes para escolher)
        viatura_service = ViaturaService(viatura_repo, cliente_repo, ot_repo)
        viatura_view = ViaturaView(raiz, self.cliente_controller.listar_clientes)
        self.viatura_controller = ViaturaController(viatura_service, viatura_view, token)

        # Técnicos e peças
        self.tecnico_controller = TecnicoController(TecnicoService(tecnico_repo), token)
        self.peca_controller = PecaController(PecaService(peca_repo), token)

        self.utilizador_service = UtilizadorService(utilizador_repo)
        self.utilizador_controller = UtilizadorController(self.utilizador_service, token)

        # Ordens de trabalho (o service das linhas usa o service das OTs)
        log_service = LogAlteracaoOTService(log_repo, ot_repo)
        ot_service = OrdemTrabalhoService(ot_repo, log_service)
        linha_service = LinhaOTService(linha_repo, ot_service)
        self.ot_controller = OrdemTrabalhoController(ot_service, token)
        self.linha_controller = LinhaOTController(linha_service, token)

        # Faturação
        self.fatura_controller = FaturaController(FaturaService(fatura_repo), token)
        self.fatura_view = FaturaView(raiz, self.fatura_controller)

        # Registo de alterações das OTs
        log_view = LogAlteracaoOTView(raiz)
        self.log_controller = LogAlteracaoOTController(log_service, log_view, token)

        perfil = self.utilizador["perfil"]

        entradas = []

        if perfil == "administrador":
            entradas = [
                ("Gestão de clientes", self.cliente_view.menu),
                ("Gestão de viaturas", self.viatura_controller.menu),
                ("Gestão de técnicos", self.abrir_tecnicos),
                ("Gestão de utilizadores", self.abrir_utilizadores),
                ("Gestão de peças", self.abrir_pecas),
                ("Ordens de trabalho", self.abrir_ots),
                ("Faturação", self.fatura_view.menu),
                ("Registo de alterações", self.log_controller.menu),
            ]

        elif perfil == "rececionista":
            entradas = [
                ("Gestão de clientes", self.cliente_view.menu),
                ("Gestão de viaturas", self.viatura_controller.menu),
                ("Gestão de peças", self.abrir_pecas),
                ("Ordens de trabalho", self.abrir_ots),
                ("Faturação", self.fatura_view.menu),
            ]

        elif perfil == "tecnico":
            entradas = [
                ("Gestão de viaturas", self.viatura_controller.menu),
                ("Gestão de peças", self.abrir_pecas),
                ("Ordens de trabalho", self.abrir_ots),
            ]
        
        # Cria o menu principal e disponibiliza a função de consulta do sumário.
        MenuPrincipalView(raiz, entradas, self.obter_sumario)

    # Obtém as estatísticas necessárias para o painel de sumário.
    def obter_sumario(self):
        perfil = self.utilizador["perfil"]

        # Consulta todas as ordens de trabalho.
        sucesso, ordens = self.ot_controller.listar_todas()

        if not sucesso:
            raise ValueError(ordens)

        # Conta as OTs que ainda não foram concluídas nem entregues.
        ordens_abertas = sum(
            1 for ot in ordens
            if ot.estado not in ("Concluída", "Entregue")
        )

        sumario = {
            "ordens_abertas": ordens_abertas
        }

        # Estatísticas disponíveis para administrador e rececionista.
        if perfil in ("administrador", "rececionista"):
            clientes = self.cliente_controller.listar_clientes()
            sumario["clientes"] = len(clientes)

        # Estatísticas disponíveis apenas para o administrador.
        if perfil == "administrador":
            faturas = self.fatura_controller.listar_faturas()

            faturas_pendentes = sum(
                1 for fatura in faturas
                if not fatura.pago
            )

            sumario["faturas_pendentes"] = faturas_pendentes

        return sumario

    def abrir_tecnicos(self):
        self.janela_tecnicos = self.abrir_pagina(
            self.janela_tecnicos, "Gestão de Técnicos", 760, 520,
            TecnicoView, self.tecnico_controller)

    def abrir_utilizadores(self):
        self.janela_utilizadores = self.abrir_pagina(
            self.janela_utilizadores, "Gestão de Utilizadores", 760, 520,
            UtilizadorView, self.utilizador_controller)

    def abrir_pecas(self):
        self.janela_pecas = self.abrir_pagina(
            self.janela_pecas, "Gestão de Peças", 900, 700,
            PecaView, self.peca_controller)

    # Os módulos de técnicos e peças são "páginas" (ttk.Frame): aqui ficam numa janela
    # própria com o mesmo cabeçalho das outras. Se já estiver aberta, passa para a frente.
    def abrir_pagina(self, janela, titulo, largura, altura, classe_view, controller):
        if janela is not None and janela.winfo_exists():
            janela.lift()
            return janela
        janela = criar_janela(self.raiz, "AutoXpert - " + titulo, largura, altura)
        criar_cabecalho(janela, titulo)
        pagina = classe_view(janela, controller)
        pagina.pack(fill="both", expand=True)
        return janela

    def abrir_ots(self):
        # Se a janela já estiver aberta, traz-a para a frente
        if self.janela_ots is not None and self.janela_ots.winfo_exists():
            self.janela_ots.lift()
            return
        self.janela_ots = tk.Toplevel(self.raiz)
        JanelaOTs(self.janela_ots, self.ot_controller, self.linha_controller)

    def fechar(self):
        self.conexao.close()



# Quantas vezes se pode errar no login antes de a aplicação fechar
MAX_TENTATIVAS_LOGIN = 3


def main():
    inicializar_bd()

    raiz = tk.Tk()
    aplicar_tema(raiz)

    conn = get_connection()

    total_utilizadores = conn.execute(
        "SELECT COUNT(*) FROM utilizadores"
    ).fetchone()[0]

    estado = {
        "primeiro_acesso": total_utilizadores == 0,
        "tentativas": 0,
        "aplicacao": None,
        "autenticacao": None
    }

    def limpar_janela():
        # Remove todos os elementos visuais da janela atual.
        for widget in raiz.winfo_children():
            widget.destroy()

    def mostrar_autenticacao(primeiro_acesso):
        estado["primeiro_acesso"] = primeiro_acesso

        limpar_janela()

        estado["autenticacao"] = AutenticacaoView(
            raiz,
            primeiro_acesso,
            ao_submeter
        )

    def iniciar_aplicacao(utilizador):
        token = criar_token(
            utilizador["login"],
            utilizador["perfil"]
        )

        # Validamos o token antes de abrir os módulos.
        validar_token(token)

        limpar_janela()

        try:
            estado["aplicacao"] = AplicacaoAutoXpert(raiz, token)
        except Exception as erro:
            messagebox.showerror(
                "AutoXpert",
                "Não foi possível iniciar a aplicação:\n" + str(erro),
                parent=raiz
            )
            raiz.destroy()

    def ao_submeter(login, senha, confirmacao):
        if not login or not senha:
            estado["autenticacao"].mostrar_mensagem(
                "Preencha todos os campos."
            )
            return

        # Primeiro acesso: criação obrigatória do administrador inicial.
        if estado["primeiro_acesso"]:
            if senha != confirmacao:
                estado["autenticacao"].mostrar_mensagem(
                    "As palavras-passe não coincidem."
                )
                return

            try:
                registar_utilizador(
                    conn,
                    login,
                    senha,
                    "administrador"
                )
            except Exception as erro:
                estado["autenticacao"].mostrar_mensagem(str(erro))
                return

            messagebox.showinfo(
                "AutoXpert",
                "Administrador criado com sucesso. Já pode iniciar sessão.",
                parent=raiz
            )

            mostrar_autenticacao(False)
            return

        # Login normal.
        utilizador = autenticar(conn, login, senha)

        if utilizador is None:
            estado["tentativas"] += 1

            restantes = (
                MAX_TENTATIVAS_LOGIN - estado["tentativas"]
            )

            if restantes <= 0:
                messagebox.showerror(
                    "AutoXpert",
                    "Número máximo de tentativas atingido.",
                    parent=raiz
                )
                raiz.destroy()
                return

            estado["autenticacao"].mostrar_mensagem(
                f"Credenciais inválidas. Tentativas restantes: {restantes}."
            )
            estado["autenticacao"].limpar_campos()
            return

        # Credenciais corretas: abrir a aplicação com o perfil do utilizador.
        iniciar_aplicacao(utilizador)

    # Mostra o formulário adequado ao estado da base de dados.
    mostrar_autenticacao(estado["primeiro_acesso"])

    raiz.deiconify()

    try:
        raiz.mainloop()
    finally:
        conn.close()

        if estado["aplicacao"] is not None:
            estado["aplicacao"].fechar()


if __name__ == "__main__":
    main()
