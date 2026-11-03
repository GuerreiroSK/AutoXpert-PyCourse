import unittest
from unittest.mock import MagicMock

from src.models.peca_model import Peca
from src.services.peca_service import PecaService


class TestPecaService(unittest.TestCase):
    # Testes unitários: o repositório é MagicMock, por isso não há base de dados.

    def setUp(self):
        self.mock_repo = MagicMock()
        self.svc = PecaService(self.mock_repo)

    def peca(self, **mudancas):
        peca = Peca("REF1", "Filtro", 5.0, 9.0, 3, 1, "Forn")
        for chave in mudancas:
            setattr(peca, chave, mudancas[chave])
        return peca

    # ----- guardar -----

    def test_guardar_nova_limpa_o_texto_e_insere(self):
        self.svc.guardar(self.peca(referencia=" REF1 ", nome=" Filtro ", fornecedor="  "))

        self.mock_repo.inserir.assert_called_once()
        enviada = self.mock_repo.inserir.call_args[0][0]
        self.assertEqual(enviada.referencia, "REF1")
        self.assertEqual(enviada.nome, "Filtro")
        self.assertIsNone(enviada.fornecedor)
        self.mock_repo.atualizar.assert_not_called()

    def test_guardar_rejeita_dados_invalidos(self):
        casos = [("referencia", ""), ("nome", "  "),
                 ("preco_compra", -1.0), ("preco_venda", float("nan")),
                 ("stock_atual", -1), ("stock_minimo", 1.5)]
        for campo, valor in casos:
            with self.subTest(campo=campo, valor=valor):
                with self.assertRaises(ValueError):
                    self.svc.guardar(self.peca(**{campo: valor}))
                self.mock_repo.inserir.assert_not_called()

    def test_guardar_existente_atualiza_e_devolve_a_peca_guardada(self):
        self.mock_repo.atualizar.return_value = True
        guardada = self.peca(id_peca=4)
        self.mock_repo.obter_por_id.return_value = guardada

        resultado = self.svc.guardar(self.peca(id_peca=4))

        self.mock_repo.atualizar.assert_called_once()
        self.mock_repo.inserir.assert_not_called()
        self.assertIs(resultado, guardada)

    def test_guardar_existente_inexistente_levanta_erro(self):
        self.mock_repo.atualizar.return_value = False

        with self.assertRaises(ValueError):
            self.svc.guardar(self.peca(id_peca=99))

    # ----- listar / obter -----

    def test_listar_todas_ou_so_stock_baixo(self):
        self.svc.listar()
        self.svc.listar(True)

        self.mock_repo.listar_todos.assert_called_once()
        self.mock_repo.listar_stock_baixo.assert_called_once()

    def test_obter_inexistente_levanta_erro(self):
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.obter(99)

    # ----- ajustar stock -----

    def test_ajustar_stock_chama_o_repositorio(self):
        self.mock_repo.obter_por_id.return_value = self.peca(id_peca=4, stock_atual=5)
        self.mock_repo.atualizar_stock.return_value = True

        self.svc.ajustar_stock(4, -2)

        self.mock_repo.atualizar_stock.assert_called_once_with(4, -2)

    def test_ajustar_stock_variacao_invalida(self):
        for variacao in (0, 1.5, "2", True):
            with self.subTest(variacao=variacao):
                with self.assertRaises(ValueError):
                    self.svc.ajustar_stock(4, variacao)
                self.mock_repo.atualizar_stock.assert_not_called()

    def test_ajustar_stock_nao_deixa_ficar_negativo(self):
        self.mock_repo.obter_por_id.return_value = self.peca(id_peca=4, stock_atual=1)

        with self.assertRaisesRegex(ValueError, "excede"):
            self.svc.ajustar_stock(4, -2)

        self.mock_repo.atualizar_stock.assert_not_called()

    def test_ajustar_stock_de_peca_inexistente(self):
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.ajustar_stock(99, 1)

    # ----- receber stock -----

    def test_receber_stock_chama_registar_entrada(self):
        self.mock_repo.registar_entrada.return_value = True
        self.mock_repo.obter_por_id.return_value = self.peca(id_peca=4)

        self.svc.receber_stock(4, 10, " Forn ", 6.5)

        self.mock_repo.registar_entrada.assert_called_once_with(4, 10, "Forn", 6.5)

    def test_receber_stock_rejeita_dados_invalidos(self):
        casos = [(0, "Forn", 6.5), (-1, "Forn", 6.5), (1.5, "Forn", 6.5),
                 (10, "  ", 6.5), (10, "Forn", -1.0)]
        for quantidade, fornecedor, preco in casos:
            with self.subTest(quantidade=quantidade, fornecedor=fornecedor, preco=preco):
                with self.assertRaises(ValueError):
                    self.svc.receber_stock(4, quantidade, fornecedor, preco)
                self.mock_repo.registar_entrada.assert_not_called()

    def test_receber_stock_de_peca_inexistente(self):
        self.mock_repo.registar_entrada.return_value = False

        with self.assertRaises(ValueError):
            self.svc.receber_stock(99, 10, "Forn", 6.5)

    # ----- eliminar -----

    def test_eliminar(self):
        self.mock_repo.eliminar.return_value = True

        self.svc.eliminar(4)

        self.mock_repo.eliminar.assert_called_once_with(4)

    def test_eliminar_inexistente_levanta_erro(self):
        self.mock_repo.eliminar.return_value = False

        with self.assertRaises(ValueError):
            self.svc.eliminar(99)
