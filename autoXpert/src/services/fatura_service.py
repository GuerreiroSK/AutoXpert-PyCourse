from datetime import date
from src.models.fatura_models import Fatura
from pathlib import Path
from openpyxl import Workbook

# Caminho da pasta docs do projeto / vai buscar o path da pasta atual, sobe duas pastas e adiciona docs
PASTA_DOCS = Path(__file__).resolve().parents[2] / "docs"



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

    # READ - Consultar fatura por ID
    def obter_por_id(self, id_fatura):
        fatura = self.repository.obter_por_id(id_fatura)

        if fatura is None:
            raise ValueError("Fatura não encontrada.")

        return fatura

    # UPDATE - Atualizar fatura
    def atualizar(self, fatura):

        if fatura.valor_total <= 0:
            raise ValueError("O valor da fatura tem de ser superior a zero.")

        # Verificar se a fatura existe
        fatura_existente = self.repository.obter_por_id(
            fatura.id_fatura
        )

        if fatura_existente is None:
            raise ValueError("Fatura não encontrada.")

        # Verificar se a OT já está associada a outra fatura
        outra_fatura = self.repository.obter_por_ot(fatura.id_ot)

        if outra_fatura and outra_fatura.id_fatura != fatura.id_fatura:
            raise ValueError("Esta Ordem de Trabalho já tem uma fatura.")

        # Verificar estado de pagamento
        if fatura.pago:
            if not fatura.data_pagamento:
                fatura.data_pagamento = date.today().isoformat()

            if not fatura.metodo_pagamento:
                raise ValueError("O método de pagamento é obrigatório.")

        else:
            fatura.data_pagamento = None
            fatura.metodo_pagamento = None

        return self.repository.atualizar(fatura)

    # DELETE - Eliminar fatura
    def eliminar(self, id_fatura):

        # Verificar se a fatura existe
        fatura = self.repository.obter_por_id(id_fatura)

        if fatura is None:
            raise ValueError("Fatura não encontrada.")

        return self.repository.eliminar(id_fatura)

    # CREATE - Gerar fatura por OT
    def gerar_por_ot(self, id_ot):

        # Verificar se já existe uma fatura para esta OT
        if self.repository.obter_por_ot(id_ot):
            raise ValueError("Esta OT já tem uma fatura.")

        linhas = self.repository.obter_linhas_ot(id_ot)

        if not linhas:
            raise ValueError("A OT não tem linhas registadas.")

        valor_total = 0

        for linha in linhas:

            if linha["tipo"] == "mao_obra":
                valor_total += (
                    (linha["horas_trabalhadas"] or 0)
                    * linha["preco_unitario"]
                )

            elif linha["tipo"] == "peca":
                valor_total += (
                    linha["quantidade"]
                    * linha["preco_unitario"]
                )

        valor_total = round(valor_total, 2)

        # Criar fatura através do método registar
        return self.registar(
            id_ot,
            valor_total,
            0,
            None,
            None
        )

    # EXPORT - Exportar relatório mensal
    def exportar_relatorio_mensal(self, mes, ano):
        if not 1 <= mes <= 12:
            raise ValueError("Mês inválido.")

        faturas = self.repository.listar_por_mes(mes, ano)

        # Criar a pasta docs, caso ainda não exista
        PASTA_DOCS.mkdir(parents=True, exist_ok=True)

        # Definir o nome e caminho do ficheiro
        caminho = PASTA_DOCS / f"Faturacao_{ano}_{mes:02d}.xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = "Faturação Mensal"

        ws.append([
            "ID Fatura", "ID OT", "Data Emissão", "Valor Total",
            "Pago", "Data Pagamento", "Método Pagamento"
        ])

        for fatura in faturas:
            ws.append([
                fatura.id_fatura,
                fatura.id_ot,
                fatura.data_emissao,
                fatura.valor_total,
                "Sim" if fatura.pago else "Não",
                fatura.data_pagamento,
                fatura.metodo_pagamento
            ])

        wb.save(caminho)

        return caminho

    def marcar_como_paga(self, id_fatura, data_pagamento, metodo_pagamento):
        fatura = self.repository.obter_por_id(id_fatura)

        if fatura is None:
            raise ValueError("Fatura não encontrada.")

        if fatura.pago:
            raise ValueError("Esta fatura já se encontra paga.")

        if not metodo_pagamento:
            raise ValueError("O método de pagamento é obrigatório.")

        data_pagamento = data_pagamento or date.today().isoformat()

        try:
            date.fromisoformat(data_pagamento)
        except ValueError:
            raise ValueError("A data de pagamento é inválida.")

        return self.repository.marcar_como_paga(
            id_fatura, data_pagamento, metodo_pagamento
        )