import sqlite3
import unittest
from datetime import date

from src.models.ordem_trabalho_model import OrdemTrabalho
from src.models.linha_ot_model import LinhaOT
from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.repositories.linha_ot_repository import LinhaOTRepository
from src.services.ot_service import OrdemTrabalhoService
from tests.bd_testes.base_dados_teste import criar_conexao_teste


class TesteOrdemTrabalhoService(unittest.TestCase):

    def setUp(self):
        self.conexao = criar_conexao_teste()
        self.repo_ot = OrdemTrabalhoRepository(self.conexao)
        self.repo_linha = LinhaOTRepository(self.conexao)
        self.service = OrdemTrabalhoService(self.repo_ot, self.repo_linha)

    def tearDown(self):
        self.conexao.close()

    def _criar_ot(self, id_viatura=1, id_tecnico=1, data_entrada="2026-10-28",
                  data_prev_saida="2026-10-30"):
        return self.service.criar_ot(id_viatura, id_tecnico, data_entrada,
                                     data_prev_saida, "Travões a chiar")

    # OT que passou por Concluída e Entregue (já não pode ser alterada)
    def _criar_ot_entregue(self):
        ot = self._criar_ot()
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "Trabalho", 1, 50)
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_CONCLUIDA)
        self.service.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_ENTREGUE,
                                  data_saida_real="2026-10-30")
        return ot

    def _ids(self, lista):
        resultado = []
        for ot in lista:
            resultado.append(ot.id_ot)
        return resultado

    # ----- criar_ot -----

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

    # ----- mudar_estado -----

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

    # ----- atribuir_tecnico -----

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

    # ----- adicionar_linha / remover_linha / recalcular_custo -----

    def test_adicionar_linhas_recalcula_o_custo(self):
        ot = self._criar_ot()
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA,
                                     "Substituir pastilhas", 1.5, 40.0,
                                     horas_trabalhadas=1.5)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 60.0)
        linha = self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA,
                                             "Pastilhas", 2, 25.0, id_peca=1)
        self.assertEqual(linha.id_linha, 2)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 110.0)

    def test_remover_linha_recalcula_o_custo(self):
        ot = self._criar_ot()
        l1 = self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "Trabalho", 1, 40)
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA, "Filtro", 1, 15.5, id_peca=1)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 55.5)
        self.service.remover_linha(l1.id_linha)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 15.5)
        self.assertEqual(len(self.service.listar_linhas(ot.id_ot)), 1)

    def test_remover_ultima_linha_poe_custo_a_zero(self):
        ot = self._criar_ot()
        linha = self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "Trabalho", 1, 40)
        self.service.remover_linha(linha.id_linha)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 0)

    def test_custo_e_arredondado_a_duas_casas(self):
        ot = self._criar_ot()
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA, "Parafuso", 3, 0.1, id_peca=1)
        self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA, "Porca", 3, 0.2, id_peca=2)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 0.9)

    def test_adicionar_linha_valida_os_dados(self):
        ot = self._criar_ot()
        with self.assertRaises(ValueError):   # descrição vazia
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, " ", 1, 10)
        with self.assertRaises(ValueError):   # quantidade 0
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "x", 0, 10)
        with self.assertRaises(ValueError):   # preço negativo
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "x", 1, -1)
        with self.assertRaises(ValueError):   # tipo inválido
            self.service.adicionar_linha(ot.id_ot, "outro", "x", 1, 10)
        with self.assertRaises(ValueError):   # peça sem indicar a peça
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_PECA, "x", 1, 10)
        with self.assertRaises(ValueError):   # mão-de-obra com peça
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "x", 1, 10, id_peca=1)
        self.assertEqual(self.service.listar_linhas(ot.id_ot), [])
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 0)

    def test_adicionar_linha_a_ot_inexistente(self):
        with self.assertRaises(ValueError):
            self.service.adicionar_linha(99, LinhaOT.TIPO_MAO_OBRA, "x", 1, 10)

    def test_ot_entregue_nao_aceita_nem_perde_linhas(self):
        ot = self._criar_ot_entregue()
        linhas = self.service.listar_linhas(ot.id_ot)
        with self.assertRaises(ValueError):
            self.service.adicionar_linha(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "x", 1, 10)
        with self.assertRaises(ValueError):
            self.service.remover_linha(linhas[0].id_linha)
        self.assertEqual(len(self.service.listar_linhas(ot.id_ot)), 1)
        self.assertEqual(self.repo_ot.procurar_por_id(ot.id_ot).custo_total, 50)

    def test_remover_linha_inexistente(self):
        with self.assertRaises(ValueError):
            self.service.remover_linha(99)

    # ----- consultas -----

    def test_obter_ot(self):
        ot = self._criar_ot()
        self.assertEqual(self.service.obter_ot(ot.id_ot).id_ot, ot.id_ot)
        with self.assertRaises(ValueError):
            self.service.obter_ot(99)

    def test_listar_linhas_de_ot_inexistente(self):
        with self.assertRaises(ValueError):
            self.service.listar_linhas(99)

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