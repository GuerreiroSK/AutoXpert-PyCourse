from src.models.fatura_models import Fatura
from db.connection import get_connection


class FaturaRepository:
    def inserir(self, fatura):
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO Fatura (
                    id_ot, data_emissao, valor_total,
                    pago, data_pagamento, metodo_pagamento
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    fatura.id_ot,
                    fatura.data_emissao,
                    fatura.valor_total,
                    fatura.pago,
                    fatura.data_pagamento,
                    fatura.metodo_pagamento
                )
            )

            fatura.id_fatura = cur.lastrowid

        return fatura

    def listar_todos(self):
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM Fatura ORDER BY id_fatura"
            ).fetchall()

        return [
            Fatura(
                id_fatura=r["id_fatura"],
                id_ot=r["id_ot"],
                data_emissao=r["data_emissao"],
                valor_total=r["valor_total"],
                pago=r["pago"],
                data_pagamento=r["data_pagamento"],
                metodo_pagamento=r["metodo_pagamento"]
            )
            for r in rows
        ]