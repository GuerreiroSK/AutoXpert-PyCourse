
from src.models.viatura_model import Viatura


class ViaturaController:

    def __init__(self, viatura_service, viatura_view):
        self.viatura_service = viatura_service
        self.viatura_view = viatura_view

    # -----------------------------------------
    # REGISTAR VIATURA
    # -----------------------------------------
    def registar_viatura(self):

        dados = self.viatura_view.pedir_dados_viatura()

        # Verificar se o utilizador cancelou
        if dados is None:
            return

        try:
            viatura = Viatura(
                matricula=dados["matricula"],
                marca=dados["marca"],
                modelo=dados["modelo"],
                id_cliente=int(dados["id_cliente"]),
                ano=int(dados["ano"]) if dados.get("ano") else None,
                cor=dados.get("cor"),
                km_estrada=int(dados.get("km_estrada") or 0)
            )

            self.viatura_service.registar_viatura(viatura)

            self.viatura_view.mostrar_mensagem(
                "Sucesso",
                "Viatura registada com sucesso!"
            )

        except (ValueError, KeyError, TypeError) as erro:
            self.viatura_view.mostrar_erro(
                "Erro",
                str(erro)
            )

        except Exception as erro:
            self.viatura_view.mostrar_erro(
                "Erro",
                str(erro)
            )

    # -----------------------------------------
    # CONSULTAR VIATURA
    # -----------------------------------------
    def consultar_viatura(self):

        matricula = self.viatura_view.pedir_matricula()

        # Verificar se o utilizador cancelou
        if matricula is None:
            return

        try:
            viatura = self.viatura_service.consultar_por_matricula(
                matricula
            )

            if viatura:
                self.viatura_view.mostrar_viatura(viatura)
            else:
                self.viatura_view.mostrar_erro(
                    "Aviso",
                    "Não foi encontrada nenhuma viatura com essa matrícula."
                )

        except Exception as erro:
            self.viatura_view.mostrar_erro(
                "Erro",
                str(erro)
            )

    # -----------------------------------------
    # LISTAR VIATURAS
    # -----------------------------------------
    def listar_viaturas(self):

        try:
            viaturas = self.viatura_service.listar_viaturas()

            if viaturas:
                self.viatura_view.mostrar_viaturas(viaturas)
            else:
                self.viatura_view.mostrar_mensagem(
                    "Informação",
                    "Não existem viaturas registadas."
                )

        except Exception as erro:
            self.viatura_view.mostrar_erro(
                "Erro",
                str(erro)
            )

    # -----------------------------------------
    # ATUALIZAR VIATURA
    # -----------------------------------------
    def atualizar_viatura(self):

        id_viatura = self.viatura_view.pedir_id_viatura()

        # Verificar se o utilizador cancelou
        if id_viatura is None:
            return

        try:
            id_viatura = int(id_viatura)

            viatura = self.viatura_service.consultar_por_id(
                id_viatura
            )

            if viatura is None:
                self.viatura_view.mostrar_erro(
                    "Aviso",
                    "Viatura não encontrada."
                )
                return

            dados = self.viatura_view.pedir_dados_atualizacao(
                viatura
            )

            # Verificar se o utilizador cancelou a atualização
            if dados is None:
                return

            # Atualizar apenas os campos fornecidos
            viatura.matricula = dados.get(
                "matricula", viatura.matricula
            )
            viatura.marca = dados.get(
                "marca", viatura.marca
            )
            viatura.modelo = dados.get(
                "modelo", viatura.modelo
            )
            viatura.ano = (
                int(dados["ano"])
                if dados.get("ano")
                else viatura.ano
            )
            viatura.cor = dados.get(
                "cor", viatura.cor
            )
            viatura.km_estrada = (
                int(dados["km_estrada"])
                if dados.get("km_estrada") not in (None, "")
                else viatura.km_estrada
            )

            resultado = self.viatura_service.atualizar_viatura(
                viatura
            )

            if resultado:
                self.viatura_view.mostrar_mensagem(
                    "Sucesso",
                    "Viatura atualizada com sucesso!"
                )
            else:
                self.viatura_view.mostrar_erro(
                    "Aviso",
                    "Não foi possível atualizar a viatura."
                )

        except (ValueError, TypeError) as erro:
            self.viatura_view.mostrar_erro(
                "Erro",
                str(erro)
            )

        except Exception as erro:
            self.viatura_view.mostrar_erro(
                "Erro",
                str(erro)
            )

    # -----------------------------------------
    # ELIMINAR VIATURA
    # -----------------------------------------
    def eliminar_viatura(self):

        id_viatura = self.viatura_view.pedir_id_viatura()

        # Verificar se o utilizador cancelou
        if id_viatura is None:
            return

        try:
            id_viatura = int(id_viatura)

            viatura = self.viatura_service.consultar_por_id(
                id_viatura
            )

            if viatura is None:
                self.viatura_view.mostrar_erro(
                    "Aviso",
                    "Viatura não encontrada."
                )
                return

            confirmacao = self.viatura_view.confirmar_eliminacao()

            # Verificar se o utilizador cancelou a confirmação
            if not confirmacao:
                return

            resultado = self.viatura_service.eliminar_viatura(
                id_viatura
            )

            if resultado:
                self.viatura_view.mostrar_mensagem(
                    "Sucesso",
                    "Viatura eliminada com sucesso!"
                )
            else:
                self.viatura_view.mostrar_erro(
                    "Aviso",
                    "Não foi possível eliminar a viatura."
                )

        except (ValueError, TypeError) as erro:
            self.viatura_view.mostrar_erro(
                "Erro",
                str(erro)
            )

        except Exception as erro:
            self.viatura_view.mostrar_erro(
                "Erro",
                str(erro)
            )

    # -----------------------------------------
    # CONSULTAR HISTÓRICO DA VIATURA
    # -----------------------------------------
    def consultar_historico(self):

        matricula = self.viatura_view.pedir_matricula()

        # Verificar se o utilizador cancelou
        if matricula is None:
            return

        try:
            viatura = self.viatura_service.consultar_por_matricula(
                matricula
            )

            if viatura is None:
                self.viatura_view.mostrar_erro(
                    "Aviso",
                    "Viatura não encontrada."
                )
                return

            # O service procura o histórico pela matrícula (e não pelo ID)
            historico = self.viatura_service.consultar_historico(
                matricula
            )

            if historico:
                self.viatura_view.mostrar_historico(historico)
            else:
                self.viatura_view.mostrar_mensagem(
                    "Informação",
                    "Esta viatura ainda não tem histórico de intervenções."
                )

        except Exception as erro:
            self.viatura_view.mostrar_erro(
                "Erro",
                str(erro)
            )

    # -----------------------------------------
    # MENU DE VIATURAS
    # -----------------------------------------
    def menu(self):

        self.viatura_view.menu_viatura(self)
