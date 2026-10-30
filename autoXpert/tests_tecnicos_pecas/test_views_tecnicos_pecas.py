import tkinter as tk
import unittest
from unittest.mock import Mock

from src.models.peca import Peca
from src.models.tecnico import Tecnico
from src.views.peca_view import PecaView
from src.views.tecnico_view import TecnicoView


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.janela = tk.Tk()
        self.janela.withdraw()
        self.addCleanup(self.janela.destroy)

    def test_guardar_tecnico_envia_campos_ao_controller(self):
        controller = Mock()
        controller.listar.return_value = []
        controller.guardar.return_value = Tecnico("Ana", "Motor", 20.5, True, 4)
        pagina = TecnicoView(self.janela, controller)
        pagina.campos["nome"].set("Ana")
        pagina.campos["especialidade"].set("Motor")
        pagina.campos["custo_hora"].set("20,50")

        pagina.guardar()

        controller.guardar.assert_called_once_with(
            {"nome": "Ana", "especialidade": "Motor", "custo_hora": "20,50"},
            True,
            None,
        )

    def test_guardar_peca_envia_campos_ao_controller(self):
        controller = Mock()
        controller.listar.return_value = []
        controller.guardar.return_value = Peca("F1", "Filtro", 5.0, 10.0, 2, 1, "Loja", 7)
        pagina = PecaView(self.janela, controller)
        valores = {
            "referencia": "F1",
            "nome": "Filtro",
            "preco_compra": "5",
            "preco_venda": "10",
            "stock_atual": "2",
            "stock_minimo": "1",
            "fornecedor": "Loja",
        }
        for campo, valor in valores.items():
            pagina.campos[campo].set(valor)

        pagina.guardar()

        controller.guardar.assert_called_once_with(valores, None)
