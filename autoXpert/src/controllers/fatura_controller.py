from src.rbac import require_perfil, obter_perfil


class FaturaController:

    def __init__(self, fatura_service, token=None):
        self.service = fatura_service
        self.token = token

    # Devolve o perfil do utilizador autenticado.
    def perfil_atual(self):
        return obter_perfil(self.token)

    # CREATE - Registar fatura
    @require_perfil("administrador", "rececionista")
    def registar_fatura(self, id_ot, valor_total, pago,
                        data_pagamento, metodo_pagamento):
        return self.service.registar(
            id_ot, valor_total, pago,
            data_pagamento, metodo_pagamento
        )

    # CREATE - Gerar fatura automaticamente a partir de uma OT
    @require_perfil("administrador", "rececionista")
    def gerar_fatura_por_ot(self, id_ot):
        return self.service.gerar_por_ot(id_ot)

    # READ - Listar todas as faturas
    @require_perfil("administrador", "rececionista")
    def listar_faturas(self):
        return self.service.listar_todos()

    # READ - Consultar fatura por ID
    @require_perfil("administrador", "rececionista")
    def consultar_fatura(self, id_fatura):
        return self.service.obter_por_id(id_fatura)

    # READ - Consultar detalhe de uma fatura
    @require_perfil("administrador", "rececionista")
    def consultar_detalhe(self, id_fatura):
        return self.service.obter_detalhe(id_fatura)

    # UPDATE - Atualizar fatura
    @require_perfil("administrador", "rececionista")
    def atualizar_fatura(self, fatura):
        return self.service.atualizar(fatura)

    # UPDATE - Marcar fatura como paga
    @require_perfil("administrador", "rececionista")
    def marcar_fatura_como_paga(self, id_fatura, data_pagamento, metodo_pagamento):
        return self.service.marcar_como_paga(
            id_fatura, data_pagamento, metodo_pagamento
        )

    # DELETE - Eliminar fatura
    @require_perfil("administrador", "rececionista")
    def eliminar_fatura(self, id_fatura):
        return self.service.eliminar(id_fatura)

    # EXPORT - Exportar relatório mensal para Excel
    @require_perfil("administrador", "rececionista")
    def exportar_relatorio_mensal(self, mes, ano):
        return self.service.exportar_relatorio_mensal(mes, ano)
