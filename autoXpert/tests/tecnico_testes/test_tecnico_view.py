import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

from src.models.tecnico_model import Tecnico
from src.views.tecnico_view import TecnicoView


class TestTecnicoView(unittest.TestCase):
    # Estes testes abrem uma janela Tk (escondida), por isso precisam de ambiente gráfico.

    def setUp(self):
        self.janela = tk.Tk()
        self.janela.withdraw()
        self.addCleanup(self.janela.destroy)

        self.controller = MagicMock()
        self.controller.listar.return_value = []

    def test_guardar_envia_os_campos_ao_controller(self):
        self.controller.guardar.return_value = Tecnico("Ana", "Motor", 20.5, True, 4)
        pagina = TecnicoView(self.janela, self.controller)
        pagina.campos["nome"].set("Ana")
        pagina.campos["especialidade"].set("Motor")
        pagina.campos["custo_hora"].set("20,50")

        pagina.guardar()

        self.controller.guardar.assert_called_once_with(
            {"nome": "Ana", "especialidade": "Motor", "custo_hora": "20,50"},
            True,
            None)

    def test_erro_ao_guardar_mantem_o_formulario(self):
        self.controller.guardar.side_effect = ValueError("Custo/hora inválido.")
        pagina = TecnicoView(self.janela, self.controller)
        pagina.campos["nome"].set("Ana")
        pagina.campos["custo_hora"].set("vinte")

        with self.assertRaises(ValueError):
            pagina.guardar()

        self.assertEqual(pagina.campos["nome"].get(), "Ana")
        self.assertEqual(pagina.campos["custo_hora"].get(), "vinte")

    def test_botao_guardar_mostra_o_erro_num_aviso(self):
        self.controller.guardar.side_effect = ValueError("Custo/hora inválido.")
        pagina = TecnicoView(self.janela, self.controller)

        with patch("src.views.estilo.messagebox.showerror") as aviso:
            pagina.clicar_guardar()

        aviso.assert_called_once()
        self.assertIn("Custo/hora inválido.", aviso.call_args[0])

    def test_eliminar_sem_selecao_levanta_erro(self):
        pagina = TecnicoView(self.janela, self.controller)

        with self.assertRaises(ValueError):
            pagina.eliminar()

        self.controller.eliminar.assert_not_called()

    def test_eliminar_confirmado_chama_o_controller(self):
        pagina = TecnicoView(self.janela, self.controller)
        pagina.id_selecionado = 4

        with patch("src.views.estilo.messagebox.askyesno", return_value=True):
            pagina.eliminar()

        self.controller.eliminar.assert_called_once_with(4)
        self.assertIsNone(pagina.id_selecionado)
        self.assertEqual(pagina.estado.get(), "Técnico eliminado.")

    def test_eliminar_cancelado_nao_chama_o_controller(self):
        pagina = TecnicoView(self.janela, self.controller)
        pagina.id_selecionado = 4

        with patch("src.views.estilo.messagebox.askyesno", return_value=False):
            pagina.eliminar()

        self.controller.eliminar.assert_not_called()
        self.assertEqual(pagina.id_selecionado, 4)

    def test_carregar_mostra_os_tecnicos_na_lista(self):
        self.controller.listar.return_value = [
            Tecnico("Ana", None, 20.0, True, 1), Tecnico("Rui", "Motor", 30.5, False, 2)]

        pagina = TecnicoView(self.janela, self.controller)

        self.assertEqual(len(pagina.lista.get_children()), 2)
        valores = pagina.lista.item("2")["values"]
        self.assertEqual(valores[1], "Rui")
        self.assertEqual(valores[4], "Não")
