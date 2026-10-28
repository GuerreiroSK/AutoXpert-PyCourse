class FaturaController:
    def __init__(self, fatura_service):
        self.service = fatura_service

    def registar_fatura(
        self, id_ot, valor_total, pago,
        data_pagamento, metodo_pagamento
    ):
        return self.service.registar(
            id_ot, valor_total, pago,
            data_pagamento, metodo_pagamento
        )

    def listar_faturas(self):
        return self.service.listar_todos()