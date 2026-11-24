from src.rbac import require_perfil


class LogAlteracaoOTController:

    def __init__(self, log_service, log_view, token=None):
        self.log_service = log_service
        self.log_view = log_view
        self.token = token

    @require_perfil("administrador")
    def consultar_alteracao(self):
        try:
            id_log = self.log_view.pedir_id_log()

            if id_log is None:
                return

            registo = self.log_service.consultar_alteracao(id_log)
            self.log_view.mostrar_alteracao(registo)

        except Exception as erro:
            self.log_view.mostrar_erro(str(erro))

    @require_perfil("administrador")
    def listar_alteracoes_por_ot(self):
        try:
            id_ot = self.log_view.pedir_id_ot()

            if id_ot is None:
                return

            registos = self.log_service.listar_alteracoes_por_ot(id_ot)
            self.log_view.mostrar_alteracoes(registos)

        except Exception as erro:
            self.log_view.mostrar_erro(str(erro))

    @require_perfil("administrador")
    def listar_todas_alteracoes(self):
        try:
            registos = self.log_service.listar_todas_alteracoes()
            self.log_view.mostrar_alteracoes(registos)

        except Exception as erro:
            self.log_view.mostrar_erro(str(erro))

    @require_perfil("administrador")
    def menu(self):
        self.log_view.menu_log(self)
