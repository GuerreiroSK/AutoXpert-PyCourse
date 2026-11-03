import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

from src.models.peca_model import Peca
from src.views.peca_view import PecaView


class TestPecaView(unittest.TestCase):
    # Estes testes abrem uma janela Tk (escondida), por isso precisam de ambiente gráfico.

    def setUp(self):
        self.janela = tk.Tk()
        self.janela.withdraw()
        self.addCleanup(self.janela.destroy)

        self.controller = MagicMock()
        self.controller.listar.return_value = []

    def pagina(self):
        return PecaView(self.janela, self.controller)

    def test_guardar_envia_os_campos_ao_controller(self):
        self.controller.guardar.return_value = Peca("R", "N", 1.0, 2.0, 0, 0, None, 4)
        pagina = self.pagina()
        pagina.campos["referencia"].set("REF1")
        pagina.campos["nome"].set("Filtro")

        pagina.guardar()

        dados = self.controller.guardar.call_args[0][0]
        self.assertEqual(dados["referencia"], "REF1")
        self.assertEqual(dados["nome"], "Filtro")
        self.assertIsNone(self.controller.guardar.call_args[0][1])
        self.assertEqual(pagina.estado.get(), "Peça 4 guardada.")

    def test_erro_ao_guardar_aparece_num_aviso_e_mantem_o_formulario(self):
        self.controller.guardar.side_effect = ValueError("Nome é obrigatório.")
        pagina = self.pagina()
        pagina.campos["referencia"].set("REF1")

        with patch("src.views.estilo.messagebox.showerror") as aviso:
            pagina.clicar_guardar()

        aviso.assert_called_once()
        self.assertIn("Nome é obrigatório.", aviso.call_args[0])
        self.assertEqual(pagina.campos["referencia"].get(), "REF1")

    def test_movimentos_sem_selecao_levantam_erro(self):
        pagina = self.pagina()

        for acao in (pagina.receber_stock, pagina.ajustar_stock, pagina.eliminar):
            with self.subTest(acao=acao.__name__):
                with self.assertRaises(ValueError):
                    acao()

        self.controller.receber_stock.assert_not_called()
        self.controller.ajustar_stock.assert_not_called()
        self.controller.eliminar.assert_not_called()

    def test_ajustar_stock_usa_o_valor_do_movimento(self):
        self.controller.ajustar_stock.return_value = Peca("R", "N", 1.0, 2.0, 7, 0, None, 4)
        pagina = self.pagina()
        pagina.id_selecionado = 4
        pagina.movimento.set("-3")

        pagina.ajustar_stock()

        self.controller.ajustar_stock.assert_called_once_with(4, "-3")
        self.assertEqual(pagina.estado.get(), "Stock da peça 4 ajustado para 7.")

    def test_receber_stock_envia_fornecedor_e_preco(self):
        self.controller.receber_stock.return_value = Peca("R", "N", 1.0, 2.0, 12, 0, None, 4)
        pagina = self.pagina()
        pagina.id_selecionado = 4
        pagina.movimento.set("10")
        pagina.campos["fornecedor"].set("Forn")
        pagina.campos["preco_compra"].set("6,5")

        pagina.receber_stock()

        self.controller.receber_stock.assert_called_once_with(4, "10", "Forn", "6,5")

    def test_eliminar_cancelado_nao_chama_o_controller(self):
        pagina = self.pagina()
        pagina.id_selecionado = 4

        with patch("src.views.estilo.messagebox.askyesno", return_value=False):
            pagina.eliminar()

        self.controller.eliminar.assert_not_called()

    def test_eliminar_confirmado_chama_o_controller(self):
        pagina = self.pagina()
        pagina.id_selecionado = 4

        with patch("src.views.estilo.messagebox.askyesno", return_value=True):
            pagina.eliminar()

        self.controller.eliminar.assert_called_once_with(4)
        self.assertEqual(pagina.estado.get(), "Peça eliminada.")

    def test_lista_marca_as_pecas_com_stock_baixo(self):
        self.controller.listar.return_value = [
            Peca("R1", "Filtro", 5.0, 9.0, 1, 2, None, 1),
            Peca("R2", "Vela", 3.0, 6.0, 10, 2, None, 2)]

        pagina = self.pagina()

        self.assertEqual(pagina.lista.item("1")["values"][7], "Stock baixo")
        self.assertEqual(pagina.lista.item("2")["values"][7], "")
        self.assertIn("baixo", pagina.lista.item("1")["tags"])
