class Fatura:
    def __init__(
        self,
        id_ot,
        data_emissao,
        valor_total,
        pago=0,
        data_pagamento=None,
        metodo_pagamento=None,
        id_fatura=None
    ):
        self.id_fatura = id_fatura
        self.id_ot = id_ot
        self.data_emissao = data_emissao
        self.valor_total = valor_total
        self.pago = pago
        self.data_pagamento = data_pagamento
        self.metodo_pagamento = metodo_pagamento

    def __str__(self):
        return f"Fatura {self.id_fatura} - Ordem de Trabalho {self.id_ot}"