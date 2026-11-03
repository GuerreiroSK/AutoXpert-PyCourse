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

from src.services.tecnico_service import TecnicoService
from src.controllers.tecnico_controller import TecnicoController
from src.views.tecnico_view import TecnicoView

from src.services.peca_service import PecaService
from src.controllers.peca_controller import PecaController
from src.views.peca_view import PecaView

from src.views.estilo import aplicar_estilo, criar_janela, criar_cabecalho
from src.views.menu_principal_view import MenuPrincipalView


class AplicacaoAutoXpert:
    # Liga todas as camadas (repositório -> service -> controller -> view) de cada
    # módulo e entrega ao menu principal a função que abre cada um.

    def __init__(self, raiz):
        self.raiz = raiz
        self.janela_ots = None
        self.janela_tecnicos = None
        self.janela_pecas = None

        # Ligação partilhada pelos módulos das OTs, viaturas e registo de alterações
        self.conexao = get_connection()

        # Clientes
        cliente_service = ClienteService(ClienteRepository())
        cliente_controller = ClienteController(cliente_service)
        self.cliente_view = ClienteView(raiz, cliente_controller)

        # Viaturas (o formulário mostra a lista de clientes para escolher)
        viatura_service = ViaturaService(ViaturaRepository(self.conexao), self.conexao)
        viatura_view = ViaturaView(raiz, cliente_controller.listar_clientes)
        self.viatura_controller = ViaturaController(viatura_service, viatura_view)

        # Ordens de trabalho (o service das linhas usa o service das OTs)
        ot_service = OrdemTrabalhoService(OrdemTrabalhoRepository(self.conexao))
        linha_service = LinhaOTService(LinhaOTRepository(self.conexao), ot_service)
        self.ot_controller = OrdemTrabalhoController(ot_service)
        self.linha_controller = LinhaOTController(linha_service)

        # Faturação
        fatura_service = FaturaService(FaturaRepository())
        self.fatura_view = FaturaView(raiz, FaturaController(fatura_service))

        # Registo de alterações das OTs
        log_service = LogAlteracaoOTService(
            LogAlteracaoOTRepository(self.conexao), self.conexao)
        log_view = LogAlteracaoOTView(raiz)
        self.log_controller = LogAlteracaoOTController(log_service, log_view)

        # Técnicos e peças (os repositórios abrem a sua própria ligação)
        self.tecnico_controller = TecnicoController(TecnicoService())
        self.peca_controller = PecaController(PecaService())

        # None = módulo que ainda não existe (aparece desativado)
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


if __name__ == "__main__":
    main()
