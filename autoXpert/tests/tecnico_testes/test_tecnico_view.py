import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

from src.controllers.tecnico_controller import TecnicoController
from src.models.tecnico_model import Tecnico
from src.repositories.tecnico_repository import TecnicoRepository
from src.services.tecnico_service import TecnicoService
from src.views.tecnico_view import TecnicoView
from tests.bd_testes.base_dados_teste import criar_conexao_vazia


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

    def test_guardar_com_lista_preenchida_grava_e_mostra_novo_tecnico(self):
        conexao = criar_conexao_vazia()
        self.addCleanup(conexao.close)
        controller = TecnicoController(TecnicoService(TecnicoRepository(conexao)))
        controller.guardar({"nome": "Ana", "especialidade": "", "custo_hora": "20"}, True)
        pagina = TecnicoView(self.janela, controller)
        pagina.campos["nome"].set("Rui")
        pagina.campos["custo_hora"].set("30,50")

        with patch("src.views.estilo.messagebox.showerror") as aviso:
            pagina.clicar_guardar()

        aviso.assert_not_called()
        self.assertEqual([tecnico.nome for tecnico in controller.listar()], ["Ana", "Rui"])
        linha_ana, linha_rui = pagina.lista.get_children()
        self.assertEqual(pagina.lista.set(linha_ana, "nome"), "Ana")
        self.assertEqual(pagina.lista.set(linha_rui, "nome"), "Rui")

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
        # Com campos válidos a validação da view passa e o erro vem do controller
        pagina.campos["nome"].set("Ana")
        pagina.campos["custo_hora"].set("20")

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
