import unittest
from unittest.mock import MagicMock

from src.models.viatura_model import Viatura
from src.services.viatura_service import ViaturaService


class TestViaturaService(unittest.TestCase):
    # Testes unitários: os três repositórios (viaturas, clientes e OTs) são MagicMock,
    # por isso não há base de dados.

    def setUp(self):
        # Executado antes de CADA teste: cria mocks limpos
        self.mock_repo = MagicMock()
        self.mock_cliente_repo = MagicMock()
        self.mock_ot_repo = MagicMock()
        # Por defeito, o cliente existe
        self.mock_cliente_repo.obter_por_id.return_value = MagicMock()

        self.svc = ViaturaService(self.mock_repo, self.mock_cliente_repo,
                                  self.mock_ot_repo)

    # Cria uma viatura válida; cada teste pode mudar os campos que precisar
    def _viatura(self, matricula="AA-00-BB", marca="BMW", modelo="Serie 1",
                 id_cliente=1, id_viatura=None, km_estrada=0):
        return Viatura(matricula=matricula, marca=marca, modelo=modelo,
                       id_cliente=id_cliente, id_viatura=id_viatura,
                       ano=2020, cor="Preto", km_estrada=km_estrada)

    # ----- registar_viatura: validações (assertRaises + assert_not_called) -----

    def test_registar_sem_matricula_levanta_erro(self):
        for matricula in ("", "   "):
            with self.subTest(matricula=matricula):
                with self.assertRaises(ValueError):
                    self.svc.registar_viatura(self._viatura(matricula=matricula))
                self.mock_repo.criar.assert_not_called()

    def test_registar_sem_marca_levanta_erro(self):
        for marca in ("", "   "):
            with self.subTest(marca=marca):
                with self.assertRaises(ValueError):
                    self.svc.registar_viatura(self._viatura(marca=marca))
                self.mock_repo.criar.assert_not_called()

    def test_registar_sem_modelo_levanta_erro(self):
        for modelo in ("", "   "):
            with self.subTest(modelo=modelo):
                with self.assertRaises(ValueError):
                    self.svc.registar_viatura(self._viatura(modelo=modelo))
                self.mock_repo.criar.assert_not_called()

    def test_registar_com_cliente_invalido_levanta_erro(self):
        for id_cliente in (0, -1):
            with self.subTest(id_cliente=id_cliente):
                with self.assertRaises(ValueError):
                    self.svc.registar_viatura(self._viatura(id_cliente=id_cliente))
                self.mock_repo.criar.assert_not_called()

    def test_registar_com_km_negativos_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.svc.registar_viatura(self._viatura(km_estrada=-1))

        self.mock_repo.criar.assert_not_called()

    def test_registar_com_cliente_inexistente_levanta_erro(self):
        self.mock_cliente_repo.obter_por_id.return_value = None   # o cliente não existe

        with self.assertRaises(ValueError):
            self.svc.registar_viatura(self._viatura(id_cliente=99))

        self.mock_repo.criar.assert_not_called()

    def test_registar_com_matricula_duplicada_levanta_erro(self):
        # O repositório já tem uma viatura com esta matrícula
        self.mock_repo.obter_por_matricula.return_value = self._viatura(id_viatura=5)

        with self.assertRaises(ValueError):
            self.svc.registar_viatura(self._viatura())

        self.mock_repo.criar.assert_not_called()

    # ----- registar_viatura: caminho feliz -----

    def test_registar_chama_o_repo_uma_vez(self):
        self.mock_repo.obter_por_matricula.return_value = None   # matrícula livre

        self.svc.registar_viatura(self._viatura())

        self.mock_repo.criar.assert_called_once()

    def test_registar_passa_a_viatura_ao_repo(self):
        self.mock_repo.obter_por_matricula.return_value = None
        viatura = self._viatura(matricula="XY-12-ZW", marca="Audi", km_estrada=1500)

        self.svc.registar_viatura(viatura)

        passada = self.mock_repo.criar.call_args[0][0]
        self.assertEqual(passada.matricula, "XY-12-ZW")
        self.assertEqual(passada.marca, "Audi")
        self.assertEqual(passada.km_estrada, 1500)

    def test_registar_verifica_a_matricula_no_repo(self):
        self.mock_repo.obter_por_matricula.return_value = None

        self.svc.registar_viatura(self._viatura(matricula="XY-12-ZW"))

        self.mock_repo.obter_por_matricula.assert_called_once_with("XY-12-ZW")

    def test_registar_devolve_o_que_o_repo_devolve(self):
        self.mock_repo.obter_por_matricula.return_value = None
        self.mock_repo.criar.return_value = 42

        resultado = self.svc.registar_viatura(self._viatura())

        self.assertEqual(resultado, 42)

    def test_registar_aceita_zero_quilometros(self):
        self.mock_repo.obter_por_matricula.return_value = None

        self.svc.registar_viatura(self._viatura(km_estrada=0))

        self.mock_repo.criar.assert_called_once()

    def test_erro_da_bd_ao_registar_propaga(self):
        self.mock_repo.obter_por_matricula.return_value = None
        self.mock_repo.criar.side_effect = RuntimeError("Ligação à BD perdida")

        with self.assertRaises(RuntimeError):
            self.svc.registar_viatura(self._viatura())

    # ----- consultar_por_id (return_value) -----

    def test_consultar_por_id_devolve_a_viatura_do_repo(self):
        self.mock_repo.obter_por_id.return_value = self._viatura(id_viatura=7)

        resultado = self.svc.consultar_por_id(7)

        self.assertEqual(resultado.id_viatura, 7)
        self.mock_repo.obter_por_id.assert_called_once_with(7)

    def test_consultar_por_id_inexistente_levanta_erro(self):
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.consultar_por_id(99)

    def test_consultar_por_id_invalido_nao_chama_o_repo(self):
        for id_viatura in (0, -1):
            with self.subTest(id_viatura=id_viatura):
                with self.assertRaises(ValueError):
                    self.svc.consultar_por_id(id_viatura)
                self.mock_repo.obter_por_id.assert_not_called()

    # ----- consultar_por_matricula -----

    def test_consultar_por_matricula_devolve_a_viatura(self):
        self.mock_repo.obter_por_matricula.return_value = self._viatura(id_viatura=7)

        resultado = self.svc.consultar_por_matricula("AA-00-BB")

        self.assertEqual(resultado.marca, "BMW")
        self.mock_repo.obter_por_matricula.assert_called_once_with("AA-00-BB")

    def test_consultar_por_matricula_tira_espacos(self):
        self.mock_repo.obter_por_matricula.return_value = self._viatura(id_viatura=7)

        self.svc.consultar_por_matricula("  AA-00-BB  ")

        self.mock_repo.obter_por_matricula.assert_called_once_with("AA-00-BB")

    def test_consultar_por_matricula_vazia_nao_chama_o_repo(self):
        for matricula in ("", "   ", None):
            with self.subTest(matricula=matricula):
                with self.assertRaises(ValueError):
                    self.svc.consultar_por_matricula(matricula)
                self.mock_repo.obter_por_matricula.assert_not_called()

    def test_consultar_por_matricula_inexistente_levanta_erro(self):
        self.mock_repo.obter_por_matricula.return_value = None

        with self.assertRaises(ValueError):
            self.svc.consultar_por_matricula("ZZ-99-ZZ")

    # ----- listar_viaturas -----

    def test_listar_devolve_a_lista_do_repositorio(self):
        self.mock_repo.listar_todas.return_value = [
            self._viatura(id_viatura=1),
            self._viatura(matricula="CC-11-DD", id_viatura=2),
        ]

        resultado = self.svc.listar_viaturas()

        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[1].matricula, "CC-11-DD")
        self.mock_repo.listar_todas.assert_called_once()

    def test_listar_vazio(self):
        self.mock_repo.listar_todas.return_value = []

        self.assertEqual(self.svc.listar_viaturas(), [])

    # ----- atualizar_viatura -----

    def test_atualizar_sem_id_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.svc.atualizar_viatura(self._viatura(id_viatura=None))

        self.mock_repo.atualizar.assert_not_called()

    def test_atualizar_com_campos_vazios_levanta_erro(self):
        casos = [
            ({"matricula": ""}, "matrícula vazia"),
            ({"marca": "  "}, "marca só espaços"),
            ({"modelo": ""}, "modelo vazio"),
            ({"km_estrada": -5}, "km negativos"),
        ]
        for campos, nome in casos:
            with self.subTest(caso=nome):
                with self.assertRaises(ValueError):
                    self.svc.atualizar_viatura(self._viatura(id_viatura=1, **campos))
                self.mock_repo.atualizar.assert_not_called()

    def test_atualizar_viatura_inexistente_levanta_erro(self):
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.atualizar_viatura(self._viatura(id_viatura=99))

        self.mock_repo.atualizar.assert_not_called()

    def test_atualizar_com_matricula_de_outra_viatura_levanta_erro(self):
        self.mock_repo.obter_por_id.return_value = self._viatura(id_viatura=1)
        # A matrícula nova já pertence à viatura 2
        self.mock_repo.obter_por_matricula.return_value = self._viatura(
            matricula="CC-11-DD", id_viatura=2)

        with self.assertRaises(ValueError):
            self.svc.atualizar_viatura(self._viatura(matricula="CC-11-DD", id_viatura=1))

        self.mock_repo.atualizar.assert_not_called()

    def test_atualizar_mantendo_a_propria_matricula_e_valido(self):
        atual = self._viatura(id_viatura=1)
        self.mock_repo.obter_por_id.return_value = atual
        self.mock_repo.obter_por_matricula.return_value = atual   # é ela própria

        self.svc.atualizar_viatura(self._viatura(marca="Audi", id_viatura=1))

        self.mock_repo.atualizar.assert_called_once()

    def test_atualizar_passa_a_viatura_ao_repo(self):
        self.mock_repo.obter_por_id.return_value = self._viatura(id_viatura=1)
        self.mock_repo.obter_por_matricula.return_value = None
        nova = self._viatura(marca="Audi", modelo="A3", id_viatura=1, km_estrada=9000)

        self.svc.atualizar_viatura(nova)

        passada = self.mock_repo.atualizar.call_args[0][0]
        self.assertEqual(passada.marca, "Audi")
        self.assertEqual(passada.modelo, "A3")
        self.assertEqual(passada.km_estrada, 9000)

    def test_erro_da_bd_ao_atualizar_propaga(self):
        self.mock_repo.obter_por_id.return_value = self._viatura(id_viatura=1)
        self.mock_repo.obter_por_matricula.return_value = None
        self.mock_repo.atualizar.side_effect = RuntimeError("BD off")

        with self.assertRaises(RuntimeError):
            self.svc.atualizar_viatura(self._viatura(id_viatura=1))

    # ----- eliminar_viatura -----

    def test_eliminar_viatura_existente(self):
        self.mock_repo.obter_por_id.return_value = self._viatura(id_viatura=3)

        self.svc.eliminar_viatura(3)

        self.mock_repo.eliminar.assert_called_once_with(3)

    def test_eliminar_viatura_inexistente_levanta_erro(self):
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.eliminar_viatura(99)

        self.mock_repo.eliminar.assert_not_called()

    # ----- consultar_historico -----

    def test_historico_procura_as_ots_da_viatura(self):
        self.mock_repo.obter_por_matricula.return_value = self._viatura(id_viatura=7)
        self.mock_ot_repo.listar_por_viatura.return_value = ["ot1", "ot2"]

        resultado = self.svc.consultar_historico("AA-00-BB")

        self.assertEqual(len(resultado), 2)
        # O repositório das OTs recebe o id da viatura encontrada pela matrícula
        self.mock_ot_repo.listar_por_viatura.assert_called_once_with(7)

    def test_historico_sem_ots_devolve_lista_vazia(self):
        self.mock_repo.obter_por_matricula.return_value = self._viatura(id_viatura=7)
        self.mock_ot_repo.listar_por_viatura.return_value = []

        self.assertEqual(self.svc.consultar_historico("AA-00-BB"), [])

    def test_historico_de_viatura_inexistente_levanta_erro(self):
        self.mock_repo.obter_por_matricula.return_value = None

        with self.assertRaises(ValueError):
            self.svc.consultar_historico("ZZ-99-ZZ")

        self.mock_ot_repo.listar_por_viatura.assert_not_called()

    def test_historico_sem_matricula_levanta_erro(self):
        for matricula in ("", "   ", None):
            with self.subTest(matricula=matricula):
                with self.assertRaises(ValueError):
                    self.svc.consultar_historico(matricula)
                self.mock_ot_repo.listar_por_viatura.assert_not_called()
