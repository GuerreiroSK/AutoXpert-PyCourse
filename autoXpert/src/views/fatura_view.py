
import sqlite3


class FaturaView:
    def __init__(self, fatura_controller):
        self.controller = fatura_controller

    def menu(self):
        while True:
            print("\n--- Gestão de Faturas ---")
            print("1 - Registar fatura")
            print("2 - Listar faturas")
            print("0 - Voltar ao menu principal")

            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.adicionar_fatura()
            elif opcao == "2":
                self.listar_faturas()
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")

    def adicionar_fatura(self):
        id_ot = input("ID da ordem de trabalho: ")
        valor_total = input("Valor total (€): ")
        pago = input("Está paga? (1 - Sim / 0 - Não): ")

        data_pagamento = None
        metodo_pagamento = None

        if pago == "1":
            data_pagamento = input(
                "Data de pagamento (AAAA-MM-DD, opcional): "
            )
            metodo_pagamento = input(
                "Método de pagamento (opcional): "
            )

        try:
            fatura = self.controller.registar_fatura(
                id_ot,
                valor_total,
                pago,
                data_pagamento,
                metodo_pagamento
            )

            print(
                f"\nFatura registada com sucesso! "
                f"ID: {fatura.id_fatura}"
            )

        except ValueError as erro:
            print(f"Erro: {erro}")

        except sqlite3.IntegrityError as erro:
            print(f"Erro ao registar fatura: {erro}")

    def listar_faturas(self):
        faturas = self.controller.listar_faturas()

        if not faturas:
            print("\nNão existem faturas registadas.")
            return

        print("\n--- Lista de Faturas ---")

        for fatura in faturas:
            estado = "Paga" if fatura.pago == 1 else "Por pagar"

            print(
                f"ID: {fatura.id_fatura} | "
                f"Ordem de trabalho: {fatura.id_ot} | "
                f"Emissão: {fatura.data_emissao} | "
                f"Valor: {fatura.valor_total:.2f} € | "
                f"Estado: {estado} | "
                f"Data de pagamento: {fatura.data_pagamento} | "
                f"Método: {fatura.metodo_pagamento}"
            )
