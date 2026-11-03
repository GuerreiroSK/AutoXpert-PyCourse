class FaturaController:

    def __init__(self, fatura_service):
        self.service = fatura_service

    # CREATE - Registar fatura
    def registar_fatura(self, id_ot, valor_total, pago,
                        data_pagamento, metodo_pagamento):
        return self.service.registar(
            id_ot, valor_total, pago,
            data_pagamento, metodo_pagamento
        )

    # CREATE - Gerar fatura automaticamente a partir de uma OT
    def gerar_fatura_por_ot(self, id_ot):
        return self.service.gerar_por_ot(id_ot)

    # READ - Listar todas as faturas
    def listar_faturas(self):
        return self.service.listar_todos()

    # READ - Consultar fatura por ID
    def consultar_fatura(self, id_fatura):
        return self.service.obter_por_id(id_fatura)

    # UPDATE - Atualizar fatura
    def atualizar_fatura(self, fatura):
        return self.service.atualizar(fatura)

    # UPDATE - Marcar fatura como paga
    def marcar_fatura_como_paga(self, id_fatura, data_pagamento, metodo_pagamento):
        return self.service.marcar_como_paga(
            id_fatura, data_pagamento, metodo_pagamento
        )

    # DELETE - Eliminar fatura
    def eliminar_fatura(self, id_fatura):
        return self.service.eliminar(id_fatura)

    # EXPORT - Exportar relatório mensal para Excel
    def exportar_relatorio_mensal(self, mes, ano):
        return self.service.exportar_relatorio_mensal(mes, ano)