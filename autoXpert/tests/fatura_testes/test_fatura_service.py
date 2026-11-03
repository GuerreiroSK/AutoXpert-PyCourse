
import unittest
from unittest.mock import MagicMock
from datetime import date

from src.services.fatura_service import FaturaService
from src.models.fatura_model import Fatura


class TestFaturaService(unittest.TestCase):

    def setUp(self):
        # Criar um Repository simulado para evitar acesso à base de dados
        self.mock_repo = MagicMock()
        self.svc = FaturaService(self.mock_repo)

    # CREATE - Registar fatura

    def test_registar_fatura_com_dados_validos(self):
        # Registar uma fatura não paga com dados válidos
        self.svc.registar(1, 150.50, 0, None, None)

        self.mock_repo.inserir.assert_called_once()

        # Obter a fatura criada pelo Service
        fatura = self.mock_repo.inserir.call_args[0][0]

        # Confirmar os dados da fatura
        self.assertEqual(fatura.id_ot, 1)
        self.assertEqual(fatura.valor_total, 150.50)
        self.assertEqual(fatura.pago, 0)
        self.assertIsNone(fatura.data_pagamento)
        self.assertIsNone(fatura.metodo_pagamento)

    def test_registar_fatura_com_id_ot_invalido_levanta_erro(self):
        # O ID da OT tem de ser um valor numérico
        with self.assertRaises(ValueError):
            self.svc.registar("abc", 150, 0, None, None)

        self.mock_repo.inserir.assert_not_called()

    def test_registar_fatura_com_id_ot_negativo_levanta_erro(self):
        # O ID da OT tem de ser positivo
        with self.assertRaises(ValueError):
            self.svc.registar(-1, 150, 0, None, None)

        self.mock_repo.inserir.assert_not_called()

    def test_registar_fatura_com_valor_negativo_levanta_erro(self):
        # O valor total da fatura não pode ser negativo
        with self.assertRaises(ValueError):
            self.svc.registar(1, -50, 0, None, None)

        self.mock_repo.inserir.assert_not_called()

    def test_registar_fatura_com_estado_pagamento_invalido(self):
        # O campo pago só aceita 0 (não pago) ou 1 (pago)
        with self.assertRaises(ValueError):
            self.svc.registar(1, 150, 2, None, None)

        self.mock_repo.inserir.assert_not_called()

    def test_registar_fatura_paga_define_data_pagamento(self):
        # Quando a fatura é paga, deve ser definida a data de pagamento
        self.svc.registar(1, 150, 1, None, "Multibanco")

        fatura = self.mock_repo.inserir.call_args[0][0]

        self.assertEqual(fatura.pago, 1)
        self.assertEqual(fatura.data_pagamento, date.today().isoformat())
        self.assertEqual(fatura.metodo_pagamento, "Multibanco")

    # READ - Listar faturas

    def test_listar_devolve_lista_do_repo(self):
        # Simular duas faturas devolvidas pelo Repository
        lista = [
            Fatura(
                id_fatura=1, id_ot=1, data_emissao="2026-11-03",
                valor_total=150, pago=0,
                data_pagamento=None, metodo_pagamento=None
            ),
            Fatura(
                id_fatura=2, id_ot=2, data_emissao="2026-11-03",
                valor_total=200, pago=1,
                data_pagamento="2026-11-03",
                metodo_pagamento="Multibanco"
            )
        ]

        self.mock_repo.listar_todos.return_value = lista

        resultado = self.svc.listar_todos()

        # Confirmar que as duas faturas foram devolvidas
        self.assertEqual(len(resultado), 2)
        self.mock_repo.listar_todos.assert_called_once()

    # READ - Consultar fatura por ID

    def test_obter_fatura_existente(self):
        # Simular uma fatura existente com ID 1
        fatura = Fatura(
            id_fatura=1, id_ot=1, data_emissao="2026-11-03",
            valor_total=150, pago=0,
            data_pagamento=None, metodo_pagamento=None
        )

        self.mock_repo.obter_por_id.return_value = fatura

        resultado = self.svc.obter_por_id(1)

        # Confirmar que foi devolvida a fatura correta
        self.assertEqual(resultado.id_fatura, 1)
        self.mock_repo.obter_por_id.assert_called_once_with(1)

    def test_obter_fatura_inexistente_levanta_erro(self):
        # Simular uma fatura que não existe
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.obter_por_id(999)

    # UPDATE - Atualizar fatura

    def test_atualizar_fatura_com_valor_zero_levanta_erro(self):
        # O Service não permite atualizar uma fatura com valor zero
        fatura = Fatura(
            id_fatura=1, id_ot=1, data_emissao="2026-11-03",
            valor_total=0, pago=0,
            data_pagamento=None, metodo_pagamento=None
        )

        with self.assertRaises(ValueError):
            self.svc.atualizar(fatura)

        self.mock_repo.atualizar.assert_not_called()

    def test_atualizar_fatura_inexistente_levanta_erro(self):
        # Simular que a fatura não existe
        fatura = Fatura(
            id_fatura=999, id_ot=1, data_emissao="2026-11-03",
            valor_total=150, pago=0,
            data_pagamento=None, metodo_pagamento=None
        )

        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.atualizar(fatura)

        self.mock_repo.atualizar.assert_not_called()

    def test_atualizar_fatura_com_ot_duplicada_levanta_erro(self):
        # Simular outra fatura associada à mesma OT
        fatura = Fatura(
            id_fatura=1, id_ot=2, data_emissao="2026-11-03",
            valor_total=150, pago=0,
            data_pagamento=None, metodo_pagamento=None
        )

        outra_fatura = Fatura(
            id_fatura=2, id_ot=2, data_emissao="2026-11-03",
            valor_total=200, pago=0,
            data_pagamento=None, metodo_pagamento=None
        )

        # Simular as respostas dos dois métodos do Repository
        self.mock_repo.obter_por_id.return_value = fatura
        self.mock_repo.obter_por_ot.return_value = outra_fatura

        with self.assertRaises(ValueError):
            self.svc.atualizar(fatura)

        self.mock_repo.atualizar.assert_not_called()

    # UPDATE - Marcar fatura como paga

    def test_marcar_fatura_como_paga(self):
        # Simular uma fatura que ainda não foi paga
        self.mock_repo.obter_por_id.return_value = MagicMock(pago=0)

        self.svc.marcar_como_paga(1, "2026-11-03", "Multibanco")

        # Confirmar que o Repository recebeu os dados do pagamento
        self.mock_repo.marcar_como_paga.assert_called_once_with(
            1, "2026-11-03", "Multibanco"
        )

    def test_marcar_fatura_ja_paga_levanta_erro(self):
        # Simular uma fatura que já se encontra paga
        self.mock_repo.obter_por_id.return_value = MagicMock(pago=1)

        with self.assertRaises(ValueError):
            self.svc.marcar_como_paga(1, "2026-11-03", "Multibanco")

        self.mock_repo.marcar_como_paga.assert_not_called()

    def test_marcar_fatura_sem_metodo_pagamento_levanta_erro(self):
        # O método de pagamento é obrigatório
        self.mock_repo.obter_por_id.return_value = MagicMock(pago=0)

        with self.assertRaises(ValueError):
            self.svc.marcar_como_paga(1, "2026-11-03", "")

        self.mock_repo.marcar_como_paga.assert_not_called()

    # DELETE - Eliminar fatura

    def test_eliminar_fatura_existente(self):
        # Simular que a fatura existe antes de a eliminar
        self.mock_repo.obter_por_id.return_value = MagicMock()

        self.svc.eliminar(1)

        self.mock_repo.eliminar.assert_called_once_with(1)

    def test_eliminar_fatura_inexistente_levanta_erro(self):
        # Simular uma fatura inexistente
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.eliminar(999)

        self.mock_repo.eliminar.assert_not_called()

    # CREATE - Gerar fatura automaticamente a partir de uma OT

    def test_gerar_fatura_por_ot_calcula_valor_total(self):
        # Simular uma OT sem fatura e com duas linhas de trabalho
        self.mock_repo.obter_por_ot.return_value = None

        self.mock_repo.obter_linhas_ot.return_value = [
            {
                "tipo": "mao_obra",
                "descricao": "Reparação",
                "quantidade": 1,
                "horas_trabalhadas": 2,
                "preco_unitario": 30
            },
            {
                "tipo": "peca",
                "descricao": "Filtro de óleo",
                "quantidade": 2,
                "horas_trabalhadas": None,
                "preco_unitario": 15
            }
        ]

        # Gerar a fatura a partir das linhas da OT
        self.svc.gerar_por_ot(1)

        self.mock_repo.inserir.assert_called_once()

        fatura = self.mock_repo.inserir.call_args[0][0]

        # 2 horas x 30€ + 2 peças x 15€ = 90€
        self.assertEqual(fatura.valor_total, 90)

    def test_gerar_fatura_por_ot_sem_linhas_levanta_erro(self):
        # Uma OT sem linhas não permite gerar uma fatura
        self.mock_repo.obter_por_ot.return_value = None
        self.mock_repo.obter_linhas_ot.return_value = []

        with self.assertRaises(ValueError):
            self.svc.gerar_por_ot(1)

        self.mock_repo.inserir.assert_not_called()

    def test_gerar_fatura_para_ot_com_fatura_existente_levanta_erro(self):
        # Não permitir gerar uma segunda fatura para a mesma OT
        self.mock_repo.obter_por_ot.return_value = MagicMock()

        with self.assertRaises(ValueError):
            self.svc.gerar_por_ot(1)

        self.mock_repo.inserir.assert_not_called()
