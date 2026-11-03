
class LogAlteracaoOTController:

    def __init__(self, log_service, log_view):
        self.log_service = log_service
        self.log_view = log_view

    def registar_alteracao(self):
        dados = self.log_view.pedir_dados_alteracao()

        # O utilizador cancelou: não há nada a registar
        if dados is None:
            return

        try:
            self.log_service.registar_alteracao(
                id_ot=dados["id_ot"],
                campo_alterado=dados["campo_alterado"],
                valor_anterior=dados["valor_anterior"],
                valor_novo=dados["valor_novo"]
            )

            self.log_view.mostrar_mensagem(
                "Alteração registada com sucesso!"
            )

        except Exception as erro:
            self.log_view.mostrar_erro(str(erro))

    def consultar_alteracao(self):
        try:
            id_log = self.log_view.pedir_id_log()

            # O utilizador cancelou
            if id_log is None:
                return

            registo = self.log_service.consultar_alteracao(id_log)

            self.log_view.mostrar_alteracao(registo)

        except Exception as erro:
            self.log_view.mostrar_erro(str(erro))

    def listar_alteracoes_por_ot(self):
        try:
            id_ot = self.log_view.pedir_id_ot()

            # O utilizador cancelou
            if id_ot is None:
                return

            registos = self.log_service.listar_alteracoes_por_ot(
                id_ot
            )

            self.log_view.mostrar_alteracoes(registos)

        except Exception as erro:
            self.log_view.mostrar_erro(str(erro))

    def listar_todas_alteracoes(self):
        try:
            registos = self.log_service.listar_todas_alteracoes()

            self.log_view.mostrar_alteracoes(registos)

        except Exception as erro:
            self.log_view.mostrar_erro(str(erro))

    def menu(self):
        # A view abre a janela com os botões; cada botão chama um método deste controller
        self.log_view.menu_log(self)
