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

    # READ - Obter fatura pelo ID
    def obter_por_id(self, id_fatura):
        with get_connection() as conn:
            r = conn.execute(
                "SELECT * FROM Fatura WHERE id_fatura = ?",
                (id_fatura,)
            ).fetchone()

        if r is None:
            return None

        return Fatura(
            id_fatura=r["id_fatura"],
            id_ot=r["id_ot"],
            data_emissao=r["data_emissao"],
            valor_total=r["valor_total"],
            pago=bool(r["pago"]),
            data_pagamento=r["data_pagamento"],
            metodo_pagamento=r["metodo_pagamento"]
        )

    # READ - Obter fatura pela OT (para salvaguardar que não criamos uma fatura para uma OT que já tem fatura. Check nos Services.)
    def obter_por_ot(self, id_ot):
        with get_connection() as conn:
            r = conn.execute(
                "SELECT * FROM Fatura WHERE id_ot = ?",
                (id_ot,)
            ).fetchone()

        if r is None:
            return None

        return Fatura(
            id_fatura=r["id_fatura"],
            id_ot=r["id_ot"],
            data_emissao=r["data_emissao"],
            valor_total=r["valor_total"],
            pago=bool(r["pago"]),
            data_pagamento=r["data_pagamento"],
            metodo_pagamento=r["metodo_pagamento"]
        )

    # UPDATE - Atualizar fatura
    def atualizar(self, fatura):
        with get_connection() as conn:
            cur = conn.execute(
                """
                UPDATE Fatura
                SET id_ot = ?,
                    data_emissao = ?,
                    valor_total = ?,
                    pago = ?,
                    data_pagamento = ?,
                    metodo_pagamento = ?
                WHERE id_fatura = ?
                """,
                (
                    fatura.id_ot,
                    fatura.data_emissao,
                    fatura.valor_total,
                    fatura.pago,
                    fatura.data_pagamento,
                    fatura.metodo_pagamento,
                    fatura.id_fatura
                )
            )

        return cur.rowcount > 0

    # DELETE - Eliminar fatura
    def eliminar(self, id_fatura):
        with get_connection() as conn:
            cur = conn.execute(
                "DELETE FROM Fatura WHERE id_fatura = ?",
                (id_fatura,)
            )

        return cur.rowcount > 0

    # READ - Listar faturas de determinado mês
    # strftime - Essa expressão é uma função do SQLite que permite extrair uma parte de uma data. (ou seja, estamos a selecionar uma fatura por mes/ano)
    def listar_por_mes(self, mes, ano):
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM Fatura
                WHERE strftime('%m', data_emissao) = ?
                AND strftime('%Y', data_emissao) = ?
                ORDER BY data_emissao
                """,
                (f"{mes:02d}", str(ano))
            ).fetchall()

        return [
            Fatura(
                id_fatura=r["id_fatura"],
                id_ot=r["id_ot"],
                data_emissao=r["data_emissao"],
                valor_total=r["valor_total"],
                pago=bool(r["pago"]),
                data_pagamento=r["data_pagamento"],
                metodo_pagamento=r["metodo_pagamento"]
            )
            for r in rows
        ]


    # READ - Obter linhas de uma Ordem de Trabalho
    def obter_linhas_ot(self, id_ot):
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT tipo, descricao, quantidade,
                    horas_trabalhadas, preco_unitario
                FROM LinhaOT
                WHERE id_ot = ?
                """,
                (id_ot,)
            ).fetchall()

        return [dict(r) for r in rows] #transforma em dicionario o resultado de cada linha para calcular o valor total da fatura no Service

    def marcar_como_paga(self, id_fatura, data_pagamento, metodo_pagamento):
        with get_connection() as conn:
            cur = conn.execute(
                """
                UPDATE Fatura
                SET pago = 1,
                    data_pagamento = ?,
                    metodo_pagamento = ?
                WHERE id_fatura = ?
                """,
                (data_pagamento, metodo_pagamento, id_fatura)
            )
        return cur.rowcount > 0