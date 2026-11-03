import sqlite3
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock

from src.models.ot_model import OrdemTrabalho
from src.services.ot_service import OrdemTrabalhoService


class TestOrdemTrabalhoService(unittest.TestCase):
    # Testes unitários: o repositório é um MagicMock, por isso não há base de dados.

    def setUp(self):
        # Executado antes de CADA teste: cria um mock limpo
        self.mock_repo = MagicMock()
        self.svc = OrdemTrabalhoService(self.mock_repo)
        # Datas prontas a usar nos testes
        self.hoje = date.today().isoformat()
        self.ontem = (date.today() - timedelta(days=1)).isoformat()
        self.amanha = (date.today() + timedelta(days=1)).isoformat()

    # Cria uma OT (como se viesse do repositório) no estado indicado
    def _ot(self, estado=OrdemTrabalho.ESTADO_PENDENTE, id_ot=1, id_tecnico=1):
        return OrdemTrabalho(1, id_tecnico, self.ontem, self.amanha,
                             "Travões a chiar", estado=estado, id_ot=id_ot)

    # Faz o repositório devolver esta OT quando o service a procurar
    def _repo_devolve(self, ot):
        self.mock_repo.procurar_por_id.return_value = ot

    # ----- criar_ot: validações (assertRaises + assert_not_called) -----

    def test_criar_sem_viatura_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.svc.criar_ot(None, 1, self.hoje, self.amanha, "Avaria")
        self.mock_repo.inserir.assert_not_called()

    def test_criar_sem_tecnico_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.svc.criar_ot(1, None, self.hoje, self.amanha, "Avaria")
        self.mock_repo.inserir.assert_not_called()

    def test_criar_com_descricao_invalida_levanta_erro(self):
        casos = [("", "vazia"), ("   ", "só espaços"), (None, "None")]
        for descricao, nome in casos:
            with self.subTest(caso=nome):
                with self.assertRaises(ValueError):
                    self.svc.criar_ot(1, 1, self.hoje, self.amanha, descricao)
                self.mock_repo.inserir.assert_not_called()

    def test_criar_com_datas_invalidas_levanta_erro(self):
        casos = [
            ("28/10/2026", "formato português"),
            ("2026-13-01", "mês 13"),
            ("2026-02-30", "dia inexistente"),
            ("2026-1-5", "sem zeros"),
            ("", "vazia"),
            (None, "None"),
        ]
        for data, nome in casos:
            with self.subTest(caso=nome):
                with self.assertRaises(ValueError):
                    self.svc.criar_ot(1, 1, data, self.amanha, "Avaria")
                with self.assertRaises(ValueError):
                    self.svc.criar_ot(1, 1, self.hoje, data, "Avaria")
                self.mock_repo.inserir.assert_not_called()

    def test_criar_com_saida_anterior_a_entrada_levanta_erro(self):
        with self.assertRaises(ValueError):
            self.svc.criar_ot(1, 1, "2026-10-28", "2026-10-27", "Avaria")
        self.mock_repo.inserir.assert_not_called()

    # ----- criar_ot: caminho feliz -----

    def test_criar_chama_o_repo_uma_vez(self):
        self.svc.criar_ot(1, 1, self.hoje, self.amanha, "Avaria")
        self.mock_repo.inserir.assert_called_once()

    def test_criar_no_mesmo_dia_e_valido(self):
        self.svc.criar_ot(1, 1, self.hoje, self.hoje, "Avaria")
        self.mock_repo.inserir.assert_called_once()

    def test_criar_passa_a_ot_com_os_dados_certos(self):
        self.svc.criar_ot(3, 2, self.hoje, self.amanha, "  Ruído no motor  ")

        ot = self.mock_repo.inserir.call_args[0][0]
        self.assertEqual(ot.id_viatura, 3)
        self.assertEqual(ot.id_tecnico, 2)
        self.assertEqual(ot.data_entrada, self.hoje)
        self.assertEqual(ot.data_prev_saida, self.amanha)
        self.assertEqual(ot.descricao_avaria, "Ruído no motor")   # sem espaços
        self.assertEqual(ot.estado, "Pendente")                    # estado por defeito
        self.assertEqual(ot.custo_total, 0)
        self.assertIsNone(ot.id_ot)                                # ainda sem ID do repo

    def test_criar_devolve_a_ot_do_repositorio(self):
        ot_gravada = self._ot(id_ot=42)
        self.mock_repo.inserir.return_value = ot_gravada

        resultado = self.svc.criar_ot(1, 1, self.hoje, self.amanha, "Avaria")

        self.assertEqual(resultado.id_ot, 42)

    # ----- criar_ot: erros da base de dados (side_effect) -----

    def test_criar_com_viatura_inexistente_propaga_o_erro(self):
        self.mock_repo.inserir.side_effect = sqlite3.IntegrityError("FOREIGN KEY constraint failed")

        with self.assertRaises(sqlite3.IntegrityError):
            self.svc.criar_ot(99, 1, self.hoje, self.amanha, "Avaria")

    def test_criar_com_bd_em_baixo_propaga_o_erro(self):
        self.mock_repo.inserir.side_effect = RuntimeError("Ligação à BD perdida")

        with self.assertRaises(RuntimeError):
            self.svc.criar_ot(1, 1, self.hoje, self.amanha, "Avaria")

    # ----- mudar_estado: validações -----

    def test_mudar_estado_de_ot_inexistente_levanta_erro(self):
        self._repo_devolve(None)

        with self.assertRaises(ValueError):
            self.svc.mudar_estado(99, "Em Curso")

        self.mock_repo.mudar_estado.assert_not_called()
        self.mock_repo.atualizar.assert_not_called()

    def test_mudar_para_estado_invalido_levanta_erro(self):
        self._repo_devolve(self._ot())

        for estado in ("Cancelada", "", None, "pendente"):
            with self.subTest(estado=estado):
                with self.assertRaises(ValueError):
                    self.svc.mudar_estado(1, estado)
                self.mock_repo.mudar_estado.assert_not_called()

    def test_mudar_para_o_mesmo_estado_nao_faz_nada(self):
        self._repo_devolve(self._ot(estado="Em Curso"))

        resultado = self.svc.mudar_estado(1, "Em Curso")

        self.assertEqual(resultado.estado, "Em Curso")
        self.mock_repo.mudar_estado.assert_not_called()
        self.mock_repo.atualizar.assert_not_called()

    # ----- mudar_estado: as mudanças são flexíveis -----

    def test_estados_intermedios_podem_mudar_em_qualquer_ordem(self):
        # Em cada caso: (estado de partida, novo estado)
        casos = [
            ("Pendente", "Em Curso"),
            ("Em Curso", "Aguarda Peça"),
            ("Aguarda Peça", "Em Curso"),
            ("Em Curso", "Pendente"),      # voltar atrás, se o trabalho atrasar
            ("Concluída", "Em Curso"),     # reabrir uma OT concluída
            ("Pendente", "Concluída"),
        ]
        for partida, novo in casos:
            with self.subTest(partida=partida, novo=novo):
                self.mock_repo.reset_mock()
                self._repo_devolve(self._ot(estado=partida))

                resultado = self.svc.mudar_estado(1, novo)

                self.assertEqual(resultado.estado, novo)
                self.mock_repo.mudar_estado.assert_called_once_with(1, novo)

    def test_data_saida_real_fica_vazia_antes_de_entregue(self):
        self._repo_devolve(self._ot(estado="Em Curso"))

        resultado = self.svc.mudar_estado(1, "Concluída")

        self.assertIsNone(resultado.data_saida_real)
        self.mock_repo.atualizar.assert_not_called()

    # ----- mudar_estado: entregar -----

    def test_so_se_entrega_uma_ot_concluida(self):
        for partida in ("Pendente", "Em Curso", "Aguarda Peça"):
            with self.subTest(partida=partida):
                self.mock_repo.reset_mock()
                self._repo_devolve(self._ot(estado=partida))

                with self.assertRaises(ValueError):
                    self.svc.mudar_estado(1, "Entregue", self.hoje)

                self.mock_repo.atualizar.assert_not_called()
                self.mock_repo.mudar_estado.assert_not_called()

    def test_entregar_grava_o_estado_e_a_data_de_saida(self):
        self._repo_devolve(self._ot(estado="Concluída"))

        resultado = self.svc.mudar_estado(1, "Entregue", self.hoje)

        self.mock_repo.atualizar.assert_called_once()
        gravada = self.mock_repo.atualizar.call_args[0][0]
        self.assertEqual(gravada.estado, "Entregue")
        self.assertEqual(gravada.data_saida_real, self.hoje)
        self.assertEqual(resultado.data_saida_real, self.hoje)
        self.mock_repo.mudar_estado.assert_not_called()

    def test_entregar_sem_data_usa_a_data_de_hoje(self):
        self._repo_devolve(self._ot(estado="Concluída"))

        self.svc.mudar_estado(1, "Entregue")

        gravada = self.mock_repo.atualizar.call_args[0][0]
        self.assertEqual(gravada.data_saida_real, self.hoje)

    def test_entregar_com_data_invalida_levanta_erro(self):
        for data in ("31/10/2026", "2026-02-30", "abc"):
            with self.subTest(data=data):
                self.mock_repo.reset_mock()
                self._repo_devolve(self._ot(estado="Concluída"))

                with self.assertRaises(ValueError):
                    self.svc.mudar_estado(1, "Entregue", data)

                self.mock_repo.atualizar.assert_not_called()

    def test_entregar_com_saida_anterior_a_entrada_levanta_erro(self):
        ot = OrdemTrabalho(1, 1, "2026-10-28", "2026-10-30", "Avaria",
                           estado="Concluída", id_ot=1)
        self._repo_devolve(ot)

        with self.assertRaises(ValueError):
            self.svc.mudar_estado(1, "Entregue", "2026-10-27")

        self.mock_repo.atualizar.assert_not_called()

    def test_ot_entregue_nao_muda_de_estado(self):
        self._repo_devolve(self._ot(estado="Entregue"))

        for novo in ("Pendente", "Em Curso", "Concluída"):
            with self.subTest(novo=novo):
                with self.assertRaises(ValueError):
                    self.svc.mudar_estado(1, novo)

        self.mock_repo.mudar_estado.assert_not_called()
        self.mock_repo.atualizar.assert_not_called()

    def test_erro_da_bd_ao_mudar_estado_propaga(self):
        self._repo_devolve(self._ot(estado="Pendente"))
        self.mock_repo.mudar_estado.side_effect = RuntimeError("BD off")

        with self.assertRaises(RuntimeError):
            self.svc.mudar_estado(1, "Em Curso")

    # ----- atribuir_tecnico -----

    def test_atribuir_tecnico_chama_o_repo_com_os_ids_certos(self):
        self._repo_devolve(self._ot(id_tecnico=1))

        resultado = self.svc.atribuir_tecnico(1, 2)

        self.mock_repo.atribuir_tecnico.assert_called_once_with(1, 2)
        self.assertEqual(resultado.id_tecnico, 2)

    def test_atribuir_tecnico_casos_invalidos(self):
        # OT inexistente
        self._repo_devolve(None)
        with self.assertRaises(ValueError):
            self.svc.atribuir_tecnico(99, 2)

        # sem técnico
        self._repo_devolve(self._ot())
        with self.assertRaises(ValueError):
            self.svc.atribuir_tecnico(1, None)

        self.mock_repo.atribuir_tecnico.assert_not_called()

    def test_nao_se_troca_tecnico_de_ot_entregue(self):
        self._repo_devolve(self._ot(estado="Entregue"))

        with self.assertRaises(ValueError):
            self.svc.atribuir_tecnico(1, 2)

        self.mock_repo.atribuir_tecnico.assert_not_called()

    def test_tecnico_inexistente_propaga_o_erro_da_bd(self):
        self._repo_devolve(self._ot())
        self.mock_repo.atribuir_tecnico.side_effect = sqlite3.IntegrityError("FOREIGN KEY")

        with self.assertRaises(sqlite3.IntegrityError):
            self.svc.atribuir_tecnico(1, 99)

    # ----- atualizar_custo_total e garantir_editavel -----

    def test_atualizar_custo_total_grava_o_valor(self):
        self._repo_devolve(self._ot())

        self.svc.atualizar_custo_total(1, 123.45)

        self.mock_repo.atualizar_custo_total.assert_called_once_with(1, 123.45)

    def test_atualizar_custo_total_aceita_zero(self):
        self._repo_devolve(self._ot())

        self.svc.atualizar_custo_total(1, 0)

        self.mock_repo.atualizar_custo_total.assert_called_once_with(1, 0)

    def test_atualizar_custo_total_invalido_levanta_erro(self):
        self._repo_devolve(self._ot())

        for custo in (-1, -0.01, None):
            with self.subTest(custo=custo):
                with self.assertRaises(ValueError):
                    self.svc.atualizar_custo_total(1, custo)
                self.mock_repo.atualizar_custo_total.assert_not_called()

    def test_atualizar_custo_total_de_ot_inexistente_levanta_erro(self):
        self._repo_devolve(None)

        with self.assertRaises(ValueError):
            self.svc.atualizar_custo_total(99, 10)

        self.mock_repo.atualizar_custo_total.assert_not_called()

    def test_garantir_editavel_aceita_todos_os_estados_menos_entregue(self):
        for estado in ("Pendente", "Em Curso", "Aguarda Peça", "Concluída"):
            with self.subTest(estado=estado):
                self.svc.garantir_editavel(self._ot(estado=estado))   # não levanta erro

    def test_garantir_editavel_recusa_ot_entregue(self):
        with self.assertRaises(ValueError):
            self.svc.garantir_editavel(self._ot(estado="Entregue"))

    # ----- consultas (return_value) -----

    def test_obter_ot_devolve_a_ot_do_repositorio(self):
        self._repo_devolve(self._ot(id_ot=7))

        resultado = self.svc.obter_ot(7)

        self.assertEqual(resultado.id_ot, 7)
        self.mock_repo.procurar_por_id.assert_called_once_with(7)

    def test_obter_ot_inexistente_levanta_erro(self):
        self._repo_devolve(None)

        with self.assertRaises(ValueError):
            self.svc.obter_ot(99)

    def test_listar_em_curso_devolve_a_lista_do_repo(self):
        self.mock_repo.listar_em_curso.return_value = [self._ot(id_ot=1), self._ot(id_ot=2)]

        resultado = self.svc.listar_em_curso()

        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0].id_ot, 1)
        self.mock_repo.listar_em_curso.assert_called_once()

    def test_listar_em_curso_vazio(self):
        self.mock_repo.listar_em_curso.return_value = []

        self.assertEqual(self.svc.listar_em_curso(), [])

    def test_historico_tira_espacos_da_matricula(self):
        self.mock_repo.listar_por_matricula.return_value = [self._ot()]

        resultado = self.svc.historico_por_matricula("  AA-11-BB  ")

        self.assertEqual(len(resultado), 1)
        self.mock_repo.listar_por_matricula.assert_called_once_with("AA-11-BB")

    def test_historico_sem_matricula_levanta_erro(self):
        for matricula in ("", "   ", None):
            with self.subTest(matricula=matricula):
                with self.assertRaises(ValueError):
                    self.svc.historico_por_matricula(matricula)
                self.mock_repo.listar_por_matricula.assert_not_called()

    # ----- pesquisar_ots -----

    def test_pesquisar_sem_filtros_passa_none_ao_repo(self):
        self.mock_repo.pesquisar.return_value = []

        self.svc.pesquisar_ots()

        self.mock_repo.pesquisar.assert_called_once_with(None, None, None, None)

    def test_pesquisar_passa_os_filtros_ao_repo(self):
        self.mock_repo.pesquisar.return_value = [self._ot()]

        resultado = self.svc.pesquisar_ots("2026-10-01", "2026-10-31", "Em Curso", 2)

        self.assertEqual(len(resultado), 1)
        self.mock_repo.pesquisar.assert_called_once_with(
            "2026-10-01", "2026-10-31", "Em Curso", 2)

    def test_pesquisar_com_filtros_invalidos_levanta_erro(self):
        casos = [
            ({"data_inicio": "05/10/2026"}, "data de início inválida"),
            ({"data_fim": "2026-02-30"}, "data de fim inválida"),
            ({"data_inicio": "2026-10-20", "data_fim": "2026-10-10"}, "início depois do fim"),
            ({"estado": "Cancelada"}, "estado inválido"),
        ]
        for filtros, nome in casos:
            with self.subTest(caso=nome):
                with self.assertRaises(ValueError):
                    self.svc.pesquisar_ots(**filtros)
                self.mock_repo.pesquisar.assert_not_called()
