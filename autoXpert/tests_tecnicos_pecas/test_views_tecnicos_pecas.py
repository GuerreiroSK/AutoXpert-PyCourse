import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

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
        controller = MagicMock()
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
        
    def test_confirmar_eliminacao_chama_controller(self):
        controller = MagicMock()
        controller.listar.return_value = []
        pagina = TecnicoView(self.janela, controller)
        pagina.id_selecionado = 4

        with patch(
            "src.views.tecnico_view.messagebox.askyesno",
            return_value=True,
        ):
            pagina.eliminar()

        controller.eliminar.assert_called_once_with(4)
        self.assertIsNone(pagina.id_selecionado)
        self.assertEqual(
            pagina.estado.get(),
            "Tecnico eliminado.",
        )
        
    def test_movimentos_sem_selecao_nao_chamam_controller(self):
        controller = MagicMock()
        controller.listar.return_value = []
        pagina = PecaView(self.janela, controller)

        for acao in [pagina.receber_stock, pagina.ajustar_stock]:
            with self.subTest(acao=acao.__name__):
                controller.reset_mock()

                with self.assertRaisesRegex(
                    ValueError,
                    "Selecione primeiro uma peca",
                ):
                    acao()

                controller.receber_stock.assert_not_called()
                controller.ajustar_stock.assert_not_called()   
                
    def test_receber_stock_envia_dados_ao_controller(self):
        controller = MagicMock()
        controller.listar.return_value = []
        controller.receber_stock.return_value = Peca(
            "F1", "Filtro", 5.25, 10.0, 5, 1, "Loja", 7
        )
        pagina = PecaView(self.janela, controller)
        pagina.id_selecionado = 7
        pagina.movimento.set("3")
        pagina.campos["fornecedor"].set("Loja")
        pagina.campos["preco_compra"].set("5,25")

        pagina.receber_stock()

        controller.receber_stock.assert_called_once_with(
            7, "3", "Loja", "5,25"
        )
        self.assertEqual(
            pagina.estado.get(),
            "Entrada registada. Stock da peca 7: 5.",
        )
                
    def test_cancelar_eliminacao_nao_chama_controller(self):
        controller = MagicMock()
        controller.listar.return_value = []
        pagina = TecnicoView(self.janela, controller)
        pagina.id_selecionado = 4

        with patch(
            "src.views.tecnico_view.messagebox.askyesno",
            return_value=False,
        ) as confirmar:
            pagina.eliminar()

        confirmar.assert_called_once_with(
            "Confirmar",
            "Eliminar o tecnico selecionado?",
            parent=pagina,
        )
        controller.eliminar.assert_not_called()
        self.assertEqual(pagina.id_selecionado, 4)

    def test_erro_ao_guardar_tecnico_preserva_formulario(self):
        controller = MagicMock()
        controller.listar.return_value = []
        controller.guardar.side_effect = ValueError(
            "Custo/hora invalido."
        )
        pagina = TecnicoView(self.janela, controller)
        pagina.campos["nome"].set("Ana")
        pagina.campos["especialidade"].set("Motor")
        pagina.campos["custo_hora"].set("vinte")
        controller.listar.reset_mock()

        with self.assertRaisesRegex(
            ValueError,
            "Custo/hora invalido",
        ):
            pagina.guardar()

        controller.guardar.assert_called_once_with(
            {
                "nome": "Ana",
                "especialidade": "Motor",
                "custo_hora": "vinte",
            },
            True,
            None,
        )
        controller.listar.assert_not_called()
        self.assertEqual(pagina.campos["nome"].get(), "Ana")
        self.assertEqual(
            pagina.campos["custo_hora"].get(),
            "vinte",
        )
    def test_guardar_peca_envia_campos_ao_controller(self):
        controller = MagicMock()
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
