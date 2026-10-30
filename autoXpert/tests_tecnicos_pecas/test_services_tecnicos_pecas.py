import unittest
from unittest.mock import patch

from src.models.peca import Peca
from src.models.tecnico import Tecnico
from src.services import peca_service, tecnico_service


class TecnicoServiceTests(unittest.TestCase):
    def test_guardar_limpa_texto_e_guarda_tecnico(self):
        with patch.object(tecnico_service, "repository") as repository:
            repository.criar_tecnico.return_value = 4
            service = tecnico_service.TecnicoService()

            tecnico = service.guardar(Tecnico(" Ana ", " Motor ", 20.0))

        repository.criar_tecnico.assert_called_once_with("Ana", "Motor", 20.0, True)
        self.assertEqual(tecnico, Tecnico("Ana", "Motor", 20.0, True, 4))

    def test_guardar_rejeita_nome_vazio(self):
        with patch.object(tecnico_service, "repository") as repository:
            service = tecnico_service.TecnicoService()

            with self.assertRaises(ValueError):
                service.guardar(Tecnico(" ", None, 20.0))

        repository.criar_tecnico.assert_not_called()

    def test_listar_converte_linhas_em_tecnicos(self):
        linha = {
            "id_tecnico": 4,
            "nome": "Ana",
            "especialidade": "Motor",
            "custo_hora": 20.0,
            "ativo": 1,
        }
        with patch.object(tecnico_service, "repository") as repository:
            repository.listar_tecnicos.return_value = [linha]

            resultado = tecnico_service.TecnicoService().listar()

        self.assertEqual(resultado, [Tecnico("Ana", "Motor", 20.0, True, 4)])


class PecaServiceTests(unittest.TestCase):
    def test_guardar_limpa_texto_e_guarda_peca(self):
        linha = {
            "id_peca": 7,
            "referencia": "F1",
            "nome": "Filtro",
            "preco_compra": 5.0,
            "preco_venda": 10.0,
            "stock_atual": 2,
            "stock_minimo": 1,
            "fornecedor": None,
        }
        with patch.object(peca_service, "repository") as repository:
            repository.criar_peca.return_value = 7
            repository.obter_peca.return_value = linha

            resultado = peca_service.PecaService().guardar(
                Peca(" F1 ", " Filtro ", 5.0, 10.0, 2, 1, " ")
            )

        repository.criar_peca.assert_called_once_with("F1", "Filtro", 5.0, 10.0, 2, 1, None)
        self.assertEqual(resultado, Peca("F1", "Filtro", 5.0, 10.0, 2, 1, None, 7))

    def test_guardar_rejeita_stock_fracionario(self):
        with patch.object(peca_service, "repository") as repository:
            service = peca_service.PecaService()

            with self.assertRaises(ValueError):
                service.guardar(Peca("F1", "Filtro", 5.0, 10.0, 1.5))

        repository.criar_peca.assert_not_called()

    def test_ajustar_stock_nao_deixa_stock_negativo(self):
        linha = {
            "id_peca": 7,
            "referencia": "F1",
            "nome": "Filtro",
            "preco_compra": 5.0,
            "preco_venda": 10.0,
            "stock_atual": 1,
            "stock_minimo": 0,
            "fornecedor": None,
        }
        with patch.object(peca_service, "repository") as repository:
            repository.obter_peca.return_value = linha
            service = peca_service.PecaService()

            with self.assertRaises(ValueError):
                service.ajustar_stock(7, -2)

        repository.atualizar_stock.assert_not_called()
