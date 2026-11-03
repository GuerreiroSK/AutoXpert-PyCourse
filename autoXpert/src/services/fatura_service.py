from datetime import date
from src.models.fatura_models import Fatura


class FaturaService:
    def __init__(self, fatura_repository):
        self.repository = fatura_repository

    def registar(
        self, id_ot, valor_total, pago,
        data_pagamento, metodo_pagamento
    ):
        try:
            id_ot = int(id_ot)
            valor_total = float(valor_total)
            pago = int(pago)
        except (ValueError, TypeError):
            raise ValueError("Introduza valores numéricos válidos.")

        if id_ot <= 0:
            raise ValueError("O ID da ordem de trabalho deve ser positivo.")

        if valor_total < 0:
            raise ValueError("O valor da fatura não pode ser negativo.")

        if pago not in (0, 1):
            raise ValueError("O pagamento deve ser 0 (não pago) ou 1 (pago).")

        if pago == 1:
            data_pagamento = data_pagamento or date.today().isoformat()
        else:
            data_pagamento = None
            metodo_pagamento = None

        fatura = Fatura(
            id_ot=id_ot,
            data_emissao=date.today().isoformat(),
            valor_total=valor_total,
            pago=pago,
            data_pagamento=data_pagamento,
            metodo_pagamento=metodo_pagamento or None
        )

        return self.repository.inserir(fatura)

    def listar_todos(self):
        return self.repository.listar_todos()