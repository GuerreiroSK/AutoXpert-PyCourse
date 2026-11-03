import tkinter as tk

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

from src.repositories.peca_repository import PecaRepository
from src.services.peca_service import PecaService
from src.controllers.peca_controller import PecaController
from src.views.peca_view import PecaView

from src.views.estilo import aplicar_estilo, criar_janela, criar_cabecalho
from src.views.menu_principal_view import MenuPrincipalView


class AplicacaoAutoXpert:
    # Liga todas as camadas (repositório -> service -> controller -> view) de cada
    # módulo e entrega ao menu principal a função que abre cada um.
    # Todos os repositórios partilham a mesma ligação à base de dados.

    def __init__(self, raiz):
        self.raiz = raiz
        self.janela_ots = None
        self.janela_tecnicos = None
        self.janela_pecas = None

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

        # Clientes
        cliente_controller = ClienteController(ClienteService(cliente_repo))
        self.cliente_view = ClienteView(raiz, cliente_controller)

        # Viaturas (o formulário mostra a lista de clientes para escolher)
        viatura_service = ViaturaService(viatura_repo, cliente_repo, ot_repo)
        viatura_view = ViaturaView(raiz, cliente_controller.listar_clientes)
        self.viatura_controller = ViaturaController(viatura_service, viatura_view)

        # Técnicos e peças
        self.tecnico_controller = TecnicoController(TecnicoService(tecnico_repo))
        self.peca_controller = PecaController(PecaService(peca_repo))

        # Ordens de trabalho (o service das linhas usa o service das OTs)
        ot_service = OrdemTrabalhoService(ot_repo)
        linha_service = LinhaOTService(linha_repo, ot_service)
        self.ot_controller = OrdemTrabalhoController(ot_service)
        self.linha_controller = LinhaOTController(linha_service)

        # Faturação
        fatura_controller = FaturaController(FaturaService(fatura_repo))
        self.fatura_view = FaturaView(raiz, fatura_controller)

        # Registo de alterações das OTs
        log_service = LogAlteracaoOTService(log_repo, ot_repo)
        log_view = LogAlteracaoOTView(raiz)
        self.log_controller = LogAlteracaoOTController(log_service, log_view)

        entradas = [
            ("Gestão de clientes", self.cliente_view.menu),
            ("Gestão de viaturas", self.viatura_controller.menu),
            ("Gestão de técnicos", self.abrir_tecnicos),
            ("Gestão de peças", self.abrir_pecas),
            ("Ordens de trabalho", self.abrir_ots),
            ("Faturação", self.fatura_view.menu),
            ("Registo de alterações", self.log_controller.menu),
        ]
        MenuPrincipalView(raiz, entradas)

    def abrir_tecnicos(self):
        self.janela_tecnicos = self.abrir_pagina(
            self.janela_tecnicos, "Gestão de Técnicos", 760, 520,
            TecnicoView, self.tecnico_controller)

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


def main():
    inicializar_bd()

    raiz = tk.Tk()
    aplicar_estilo(raiz)
    aplicacao = AplicacaoAutoXpert(raiz)
    raiz.mainloop()
    aplicacao.fechar()


main()
