import sqlite3
import unittest
from datetime import date

from src.models.ordem_trabalho_model import OrdemTrabalho
from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.services.ot_service import OrdemTrabalhoService
from tests.bd_testes.base_dados_teste import criar_conexao_teste


class TesteOrdemTrabalhoService(unittest.TestCase):

    def setUp(self):
        self.conexao = criar_conexao_teste()
        self.repo_ot = OrdemTrabalhoRepository(self.conexao)
        self.service = OrdemTrabalhoService(self.repo_ot)

    def tearDown(self):
        self.conexao.close()

    def _criar_ot(self, id_viatura=1, id_tecnico=1, data_entrada="2026-10-28",
                  data_prev_saida="2026-10-30"):
        return self.service.criar_ot(id_viatura, id_tecnico, data_entrada,
                                     data_prev_saida, "Travões a chiar")

    # OT que passou por Concluída e Entregue (já não pode ser alterada)
    def _criar_ot_entregue(self):
        ot = self._criar_ot()
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_CONCLUIDA)
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_ENTREGUE,
                                  data_saida_real="2026-10-30")
        return ot

    def _ids(self, lista):
        resultado = []
        for ot in lista:
            resultado.append(ot.id_ot)
        return resultado

    def test_criar_ot(self):
        ot = self._criar_ot()
        self.assertEqual(ot.id_ot, 1)
        self.assertEqual(ot.estado, "Pendente")
        self.assertEqual(ot.custo_total, 0)
        gravada = self.repo_ot.procurar_por_id(1)
        self.assertEqual(gravada.id_tecnico, 1)
        self.assertEqual(gravada.descricao_avaria, "Travões a chiar")

    def test_criar_ot_tira_espacos_da_descricao(self):
        ot = self.service.criar_ot(1, 1, "2026-10-28", "2026-10-30", "  Ruído  ")
        self.assertEqual(ot.descricao_avaria, "Ruído")

    def test_criar_ot_sem_tecnico(self):
        with self.assertRaises(ValueError):
            self._criar_ot(id_tecnico=None)

    def test_criar_ot_sem_viatura(self):
        with self.assertRaises(ValueError):
            self._criar_ot(id_viatura=None)

    def test_criar_ot_com_datas_invalidas(self):
        with self.assertRaises(ValueError):
            self._criar_ot(data_entrada="28/10/2026")
        with self.assertRaises(ValueError):
            self._criar_ot(data_entrada="2026-1-5")      # falta o zero
        with self.assertRaises(ValueError):
            self._criar_ot(data_prev_saida="2026-02-30")  # dia inexistente
        with self.assertRaises(ValueError):
            self._criar_ot(data_entrada=None)

    def test_criar_ot_saida_anterior_a_entrada(self):
        with self.assertRaises(ValueError):
            self._criar_ot(data_entrada="2026-10-30", data_prev_saida="2026-10-28")

    def test_criar_ot_no_mesmo_dia_e_valido(self):
        ot = self._criar_ot(data_entrada="2026-10-28", data_prev_saida="2026-10-28")
        self.assertEqual(ot.id_ot, 1)

    def test_criar_ot_sem_descricao(self):
        with self.assertRaises(ValueError):
            self.service.criar_ot(1, 1, "2026-10-28", "2026-10-30", "   ")
        with self.assertRaises(ValueError):
            self.service.criar_ot(1, 1, "2026-10-28", "2026-10-30", None)

    def test_criar_ot_com_viatura_ou_tecnico_inexistente(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._criar_ot(id_viatura=99)
        with self.assertRaises(sqlite3.IntegrityError):
            self._criar_ot(id_tecnico=99)

    def test_mudancas_de_estado_sao_flexiveis(self):
        ot = self._criar_ot()
        sequencia = [OrdemTrabalho.ESTADO_EM_CURSO,
                     OrdemTrabalho.ESTADO_AGUARDA_PECA,
                     OrdemTrabalho.ESTADO_EM_CURSO,
                     OrdemTrabalho.ESTADO_PENDENTE,      # trabalho atrasou: volta atrás
                     OrdemTrabalho.ESTADO_CONCLUIDA,
                     OrdemTrabalho.ESTADO_EM_CURSO]      # reaberta
        for estado in sequencia:
            resultado = self.service.mudar_estado(ot.id_ot, estado)
            self.assertEqual(resultado.estado, estado)
            self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).estado, estado)

    def test_data_saida_real_fica_vazia_antes_de_entregue(self):
        ot = self._criar_ot()
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_CONCLUIDA)
        self.assertIsNone(self.repo_ot.procurar_por_id(ot.id_ot).data_saida_real)

    def test_entregar_preenche_a_data_de_saida_real(self):
        ot = self._criar_ot()
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_CONCLUIDA)
        resultado = self.service.mudar_estado(
            ot.id_ot, OrdemTrabalho.ESTADO_ENTREGUE, data_saida_real="2026-10-31")
        self.assertEqual(resultado.estado, "Entregue")
        gravada = self.repo_ot.procurar_por_id(ot.id_ot)
        self.assertEqual(gravada.estado, "Entregue")
        self.assertEqual(gravada.data_saida_real, "2026-10-31")

    def test_entregar_sem_data_usa_a_data_de_hoje(self):
        ot = self._criar_ot(data_entrada="2026-01-01", data_prev_saida="2026-01-05")
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_CONCLUIDA)
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_ENTREGUE)
        gravada = self.repo_ot.procurar_por_id(ot.id_ot)
        self.assertEqual(gravada.data_saida_real, date.today().isoformat())

    def test_so_se_entrega_uma_ot_concluida(self):
        ot = self._criar_ot()
        with self.assertRaises(ValueError):
            self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_ENTREGUE)
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_EM_CURSO)
        with self.assertRaises(ValueError):
            self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_ENTREGUE)
        gravada = self.repo_ot.procurar_por_id(ot.id_ot)
        self.assertEqual(gravada.estado, "Em Curso")
        self.assertIsNone(gravada.data_saida_real)

    def test_data_de_saida_real_invalida(self):
        ot = self._criar_ot(data_entrada="2026-10-28")
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_CONCLUIDA)
        with self.assertRaises(ValueError):
            self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_ENTREGUE,
                                      data_saida_real="31/10/2026")
        with self.assertRaises(ValueError):  # anterior à entrada
            self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_ENTREGUE,
                                      data_saida_real="2026-10-27")
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).estado, "Concluída")

    def test_ot_entregue_nao_muda_de_estado(self):
        ot = self._criar_ot_entregue()
        with self.assertRaises(ValueError):
            self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_EM_CURSO)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).estado, "Entregue")

    def test_mudar_para_o_mesmo_estado_nao_faz_nada(self):
        ot = self._criar_ot()
        resultado = self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_PENDENTE)
        self.assertEqual(resultado.estado, "Pendente")

    def test_mudar_estado_invalido_ou_ot_inexistente(self):
        ot = self._criar_ot()
        with self.assertRaises(ValueError):
            self.service.mudar_estado(ot.id_ot, "Concluida")
        with self.assertRaises(ValueError):
            self.service.mudar_estado(99, OrdemTrabalho.ESTADO_EM_CURSO)

    def test_atribuir_tecnico(self):
        ot = self._criar_ot(id_tecnico=1)
        resultado = self.service.atribuir_tecnico(ot.id_ot, 2)
        self.assertEqual(resultado.id_tecnico, 2)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).id_tecnico, 2)

    def test_atribuir_tecnico_casos_invalidos(self):
        ot = self._criar_ot()
        with self.assertRaises(ValueError):
            self.service.atribuir_tecnico(ot.id_ot, None)
        with self.assertRaises(ValueError):
            self.service.atribuir_tecnico(99, 1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.service.atribuir_tecnico(ot.id_ot, 77)

    def test_nao_se_troca_tecnico_de_ot_entregue(self):
        ot = self._criar_ot_entregue()
        with self.assertRaises(ValueError):
            self.service.atribuir_tecnico(ot.id_ot, 2)

    def test_obter_ot(self):
        ot = self._criar_ot()
        self.assertEqual(self.service.obter_ot(ot.id_ot).id_ot, ot.id_ot)
        with self.assertRaises(ValueError):
            self.service.obter_ot(99)

    def test_listar_em_curso(self):
        a = self._criar_ot(data_entrada="2026-10-01", data_prev_saida="2026-10-10")
        b = self._criar_ot(data_entrada="2026-10-02", data_prev_saida="2026-10-10")
        self._criar_ot()  # fica Pendente
        self.service.mudar_estado(a.id_ot, OrdemTrabalho.ESTADO_EM_CURSO)
        self.service.mudar_estado(b.id_ot, OrdemTrabalho.ESTADO_AGUARDA_PECA)
        self.assertEqual(self._ids(self.service.listar_em_curso()), [b.id_ot, a.id_ot])

    def test_historico_por_matricula(self):
        self._criar_ot(id_viatura=1)
        self._criar_ot(id_viatura=2)
        self._criar_ot(id_viatura=1, data_entrada="2026-10-29", data_prev_saida="2026-10-30")
        self.assertEqual(self._ids(self.service.historico_por_matricula(" aa-11-bb ")), [3, 1])
        self.assertEqual(self.service.historico_por_matricula("ZZ-00-ZZ"), [])
        with self.assertRaises(ValueError):
            self.service.historico_por_matricula("  ")

    def test_pesquisar_ots(self):
        a = self._criar_ot(id_tecnico=1, data_entrada="2026-10-05", data_prev_saida="2026-10-10")
        b = self._criar_ot(id_tecnico=2, data_entrada="2026-10-20", data_prev_saida="2026-10-25")
        self.service.mudar_estado(b.id_ot, OrdemTrabalho.ESTADO_EM_CURSO)
        self.assertEqual(len(self.service.pesquisar_ots()), 2)
        self.assertEqual(self._ids(self.service.pesquisar_ots(estado="Em Curso")), [b.id_ot])
        self.assertEqual(self._ids(self.service.pesquisar_ots(id_tecnico=1)), [a.id_ot])
        self.assertEqual(
            self._ids(self.service.pesquisar_ots(data_inicio="2026-10-01", data_fim="2026-10-10")),
            [a.id_ot])

    def test_pesquisar_ots_valida_os_filtros(self):
        with self.assertRaises(ValueError):
            self.service.pesquisar_ots(data_inicio="05/10/2026")
        with self.assertRaises(ValueError):
            self.service.pesquisar_ots(data_inicio="2026-10-20", data_fim="2026-10-10")
        with self.assertRaises(ValueError):
            self.service.pesquisar_ots(estado="Concluida")

    # ----- custo total e OT editável (usados pelo LinhaOTService) -----

    def test_atualizar_custo_total(self):
        ot = self._criar_ot()
        self.service.atualizar_custo_total(ot.id_ot, 123.45)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 123.45)
        self.service.atualizar_custo_total(ot.id_ot, 0)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 0)

    def test_atualizar_custo_total_casos_invalidos(self):
        ot = self._criar_ot()
        with self.assertRaises(ValueError):   # negativo
            self.service.atualizar_custo_total(ot.id_ot, -1)
        with self.assertRaises(ValueError):   # sem valor
            self.service.atualizar_custo_total(ot.id_ot, None)
        with self.assertRaises(ValueError):   # OT inexistente
            self.service.atualizar_custo_total(99, 10)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 0)

    def test_garantir_editavel(self):
        self.service.garantir_editavel(self._criar_ot())   # Pendente: não levanta erro
        entregue = self.service.obter_ot(self._criar_ot_entregue().id_ot)
        with self.assertRaises(ValueError):
            self.service.garantir_editavel(entregue)
