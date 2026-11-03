import sqlite3
import unittest
from unittest.mock import MagicMock

from src.models.linha_ot_model import LinhaOT
from src.services.linha_ot_service import LinhaOTService


class TestLinhaOTService(unittest.TestCase):
    # Testes unitários: o repositório das linhas e o service das OTs são MagicMock,
    # por isso não há base de dados.

    def setUp(self):
        # Executado antes de CADA teste: cria mocks limpos
        self.mock_repo = MagicMock()
        self.mock_ot_service = MagicMock()
        self.svc = LinhaOTService(self.mock_repo, self.mock_ot_service)

    # Cria uma linha (como se viesse do repositório)
    def _linha(self, id_linha=1, id_ot=1, quantidade=1, preco=10):
        return LinhaOT(id_ot, LinhaOT.TIPO_MAO_OBRA, "Trabalho", quantidade, preco,
                       id_linha=id_linha)

    # ----- adicionar_linha: a OT tem de existir e estar editável -----

    def test_adicionar_a_ot_inexistente_levanta_erro(self):
        self.mock_ot_service.obter_ot.side_effect = ValueError("OT não encontrada: 99")

        with self.assertRaises(ValueError):
            self.svc.adicionar_linha(99, "mao_obra", "Trabalho", 1, 10)

        self.mock_repo.inserir.assert_not_called()
        self.mock_ot_service.atualizar_custo_total.assert_not_called()

    def test_adicionar_a_ot_entregue_levanta_erro(self):
        self.mock_ot_service.garantir_editavel.side_effect = ValueError("OT já entregue")

        with self.assertRaises(ValueError):
            self.svc.adicionar_linha(1, "mao_obra", "Trabalho", 1, 10)

        self.mock_repo.inserir.assert_not_called()
        self.mock_ot_service.atualizar_custo_total.assert_not_called()

    # ----- adicionar_linha: validações (assertRaises + assert_not_called) -----

    def test_descricao_invalida_levanta_erro(self):
        for descricao in ("", "   ", None):
            with self.subTest(descricao=descricao):
                with self.assertRaises(ValueError):
                    self.svc.adicionar_linha(1, "mao_obra", descricao, 1, 10)
                self.mock_repo.inserir.assert_not_called()

    def test_quantidade_invalida_levanta_erro(self):
        for quantidade in (0, -1, -0.5, None):
            with self.subTest(quantidade=quantidade):
                with self.assertRaises(ValueError):
                    self.svc.adicionar_linha(1, "mao_obra", "Trabalho", quantidade, 10)
                self.mock_repo.inserir.assert_not_called()

    def test_preco_invalido_levanta_erro(self):
        for preco in (-1, -0.01, None):
            with self.subTest(preco=preco):
                with self.assertRaises(ValueError):
                    self.svc.adicionar_linha(1, "mao_obra", "Trabalho", 1, preco)
                self.mock_repo.inserir.assert_not_called()

    def test_preco_zero_e_valido(self):
        self.svc.adicionar_linha(1, "mao_obra", "Garantia", 1, 0)

        self.mock_repo.inserir.assert_called_once()

    def test_linha_de_peca_sem_peca_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.svc.adicionar_linha(1, "peca", "Pastilhas", 2, 25)

        self.mock_repo.inserir.assert_not_called()

    def test_linha_de_mao_de_obra_com_peca_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.svc.adicionar_linha(1, "mao_obra", "Trabalho", 1, 40, id_peca=1)

        self.mock_repo.inserir.assert_not_called()

    def test_tipo_invalido_levanta_erro(self):
        # O próprio modelo recusa tipos que não existem
        with self.assertRaises(ValueError):
            self.svc.adicionar_linha(1, "outro", "Trabalho", 1, 10)

        self.mock_repo.inserir.assert_not_called()

    # ----- adicionar_linha: caminho feliz -----

    def test_adicionar_chama_o_repo_uma_vez(self):
        self.svc.adicionar_linha(1, "mao_obra", "Trabalho", 1, 40)

        self.mock_repo.inserir.assert_called_once()

    def test_adicionar_aceita_os_dois_tipos(self):
        # (tipo, id_peca): a peça só existe nas linhas de peça
        casos = [("mao_obra", None), ("peca", 1)]
        for tipo, id_peca in casos:
            with self.subTest(tipo=tipo):
                self.mock_repo.reset_mock()

                self.svc.adicionar_linha(1, tipo, "Item", 1, 10, id_peca=id_peca)

                self.mock_repo.inserir.assert_called_once()

    def test_adicionar_passa_a_linha_com_os_dados_certos(self):
        self.svc.adicionar_linha(5, "peca", "  Pastilhas  ", 2, 25.5,
                                 horas_trabalhadas=None, id_peca=3)

        linha = self.mock_repo.inserir.call_args[0][0]
        self.assertEqual(linha.id_ot, 5)
        self.assertEqual(linha.tipo, "peca")
        self.assertEqual(linha.descricao, "Pastilhas")   # sem espaços
        self.assertEqual(linha.quantidade, 2)
        self.assertEqual(linha.preco_unitario, 25.5)
        self.assertEqual(linha.id_peca, 3)
        self.assertIsNone(linha.id_linha)                # ainda sem ID do repo

    def test_adicionar_guarda_as_horas_da_mao_de_obra(self):
        self.svc.adicionar_linha(1, "mao_obra", "Pastilhas", 1.5, 40,
                                 horas_trabalhadas=1.5)

        linha = self.mock_repo.inserir.call_args[0][0]
        self.assertEqual(linha.horas_trabalhadas, 1.5)
        self.assertIsNone(linha.id_peca)

    def test_adicionar_devolve_a_linha_criada(self):
        resultado = self.svc.adicionar_linha(1, "mao_obra", "Trabalho", 1, 40)

        self.assertEqual(resultado.descricao, "Trabalho")

    def test_adicionar_pede_a_ot_ao_service_das_ots(self):
        self.svc.adicionar_linha(7, "mao_obra", "Trabalho", 1, 40)

        self.mock_ot_service.obter_ot.assert_called_once_with(7)
        self.mock_ot_service.garantir_editavel.assert_called_once()

    # ----- adicionar_linha: recalcula o custo da OT -----

    def test_adicionar_recalcula_e_guarda_o_custo(self):
        # Depois de inserir, o repositório devolve as linhas da OT
        self.mock_repo.listar_por_ot.return_value = [
            self._linha(1, quantidade=1.5, preco=40),   # 60.0
            self._linha(2, quantidade=2, preco=25),     # 50.0
        ]

        self.svc.adicionar_linha(1, "mao_obra", "Trabalho", 1, 10)

        self.mock_repo.listar_por_ot.assert_called_once_with(1)
        self.mock_ot_service.atualizar_custo_total.assert_called_once_with(1, 110.0)

    # ----- adicionar_linha: erros da base de dados (side_effect) -----

    def test_erro_da_bd_ao_inserir_propaga_e_nao_atualiza_o_custo(self):
        self.mock_repo.inserir.side_effect = RuntimeError("Ligação à BD perdida")

        with self.assertRaises(RuntimeError):
            self.svc.adicionar_linha(1, "mao_obra", "Trabalho", 1, 40)

        self.mock_ot_service.atualizar_custo_total.assert_not_called()

    def test_peca_inexistente_propaga_o_erro_da_bd(self):
        self.mock_repo.inserir.side_effect = sqlite3.IntegrityError("FOREIGN KEY constraint failed")

        with self.assertRaises(sqlite3.IntegrityError):
            self.svc.adicionar_linha(1, "peca", "Pastilhas", 1, 25, id_peca=99)

        self.mock_ot_service.atualizar_custo_total.assert_not_called()

    # ----- remover_linha -----

    def test_remover_linha_inexistente_levanta_erro(self):
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.remover_linha(99)

        self.mock_repo.eliminar.assert_not_called()
        self.mock_ot_service.atualizar_custo_total.assert_not_called()

    def test_remover_linha_de_ot_entregue_levanta_erro(self):
        self.mock_repo.obter_por_id.return_value = self._linha(7)
        self.mock_ot_service.garantir_editavel.side_effect = ValueError("OT já entregue")

        with self.assertRaises(ValueError):
            self.svc.remover_linha(7)

        self.mock_repo.eliminar.assert_not_called()
        self.mock_ot_service.atualizar_custo_total.assert_not_called()

    def test_remover_apaga_a_linha_certa(self):
        self.mock_repo.obter_por_id.return_value = self._linha(7, id_ot=3)
        self.mock_repo.listar_por_ot.return_value = []

        self.svc.remover_linha(7)

        self.mock_repo.eliminar.assert_called_once_with(7)
        self.mock_ot_service.obter_ot.assert_called_once_with(3)

    def test_remover_recalcula_o_custo_da_ot_da_linha(self):
        self.mock_repo.obter_por_id.return_value = self._linha(7, id_ot=3)
        self.mock_repo.listar_por_ot.return_value = [self._linha(8, id_ot=3, quantidade=1, preco=15.5)]

        self.svc.remover_linha(7)

        self.mock_repo.listar_por_ot.assert_called_once_with(3)
        self.mock_ot_service.atualizar_custo_total.assert_called_once_with(3, 15.5)

    def test_remover_a_ultima_linha_poe_o_custo_a_zero(self):
        self.mock_repo.obter_por_id.return_value = self._linha(7)
        self.mock_repo.listar_por_ot.return_value = []

        self.svc.remover_linha(7)

        self.mock_ot_service.atualizar_custo_total.assert_called_once_with(1, 0)

    def test_erro_da_bd_ao_apagar_propaga_e_nao_atualiza_o_custo(self):
        self.mock_repo.obter_por_id.return_value = self._linha(7)
        self.mock_repo.eliminar.side_effect = RuntimeError("BD off")

        with self.assertRaises(RuntimeError):
            self.svc.remover_linha(7)

        self.mock_ot_service.atualizar_custo_total.assert_not_called()

    # ----- recalcular_custo -----

    def test_recalcular_soma_os_subtotais_das_linhas(self):
        self.mock_repo.listar_por_ot.return_value = [
            self._linha(1, quantidade=1.5, preco=40),   # 60.0
            self._linha(2, quantidade=1, preco=15.5),   # 15.5
            self._linha(3, quantidade=2, preco=25),     # 50.0
        ]

        total = self.svc.recalcular_custo(1)

        self.assertEqual(total, 125.5)
        self.mock_ot_service.atualizar_custo_total.assert_called_once_with(1, 125.5)

    def test_recalcular_sem_linhas_da_zero(self):
        self.mock_repo.listar_por_ot.return_value = []

        total = self.svc.recalcular_custo(1)

        self.assertEqual(total, 0)
        self.mock_ot_service.atualizar_custo_total.assert_called_once_with(1, 0)

    def test_recalcular_arredonda_a_duas_casas(self):
        # 3 x 0.1 + 3 x 0.2 dá 0.8999999... em decimal binário
        self.mock_repo.listar_por_ot.return_value = [
            self._linha(1, quantidade=3, preco=0.1),
            self._linha(2, quantidade=3, preco=0.2),
        ]

        total = self.svc.recalcular_custo(1)

        self.assertEqual(total, 0.9)

    def test_recalcular_duas_vezes_usa_as_linhas_de_cada_momento(self):
        # side_effect com lista: a 1.ª chamada devolve uma lista, a 2.ª devolve outra
        linha1 = self._linha(1, quantidade=1, preco=40)
        linha2 = self._linha(2, quantidade=1, preco=15.5)
        self.mock_repo.listar_por_ot.side_effect = [[linha1], [linha1, linha2]]

        primeiro = self.svc.recalcular_custo(1)
        segundo = self.svc.recalcular_custo(1)

        self.assertEqual(primeiro, 40)
        self.assertEqual(segundo, 55.5)
        self.assertEqual(self.mock_ot_service.atualizar_custo_total.call_count, 2)

    # ----- listar_linhas -----

    def test_listar_devolve_as_linhas_do_repositorio(self):
        self.mock_repo.listar_por_ot.return_value = [self._linha(1), self._linha(2)]

        resultado = self.svc.listar_linhas(1)

        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[1].id_linha, 2)
        self.mock_repo.listar_por_ot.assert_called_once_with(1)

    def test_listar_de_ot_sem_linhas_devolve_lista_vazia(self):
        self.mock_repo.listar_por_ot.return_value = []

        self.assertEqual(self.svc.listar_linhas(1), [])

    def test_listar_de_ot_inexistente_levanta_erro(self):
        self.mock_ot_service.obter_ot.side_effect = ValueError("OT não encontrada: 99")

        with self.assertRaises(ValueError):
            self.svc.listar_linhas(99)

        self.mock_repo.listar_por_ot.assert_not_called()
