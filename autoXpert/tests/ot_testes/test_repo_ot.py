import sqlite3
import unittest

from src.models.ordem_trabalho_model import OrdemTrabalho
from src.models.linha_ot_model import LinhaOT
from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.repositories.linha_ot_repository import LinhaOTRepository
from tests.bd_testes.base_dados_teste import criar_conexao_teste


class TesteOrdemTrabalhoRepository(unittest.TestCase):

    # Corre antes de cada teste: base de dados nova e vazia
    def setUp(self):
        self.conexao = criar_conexao_teste()
        self.repo = OrdemTrabalhoRepository(self.conexao)
        self.linhas = LinhaOTRepository(self.conexao)

    def tearDown(self):
        self.conexao.close()

    # Cria e grava uma OT, com valores por defeito que cada teste pode mudar
    def _criar(self, id_viatura=1, id_tecnico=1, data_entrada="2026-10-28",
               estado=OrdemTrabalho.ESTADO_PENDENTE):
        ot = OrdemTrabalho(id_viatura, id_tecnico, data_entrada, "2026-11-30",
                           "Avaria de teste", estado=estado)
        return self.repo.inserir(ot)

    def _ids(self, lista):
        resultado = []
        for ot in lista:
            resultado.append(ot.id_ot)
        return resultado

    # ----- CRUD -----

    def test_inserir_preenche_o_id(self):
        ot = self._criar()
        self.assertEqual(ot.id_ot, 1)
        self.assertEqual(self._criar().id_ot, 2)

    def test_procurar_por_id(self):
        ot = self._criar()
        lida = self.repo.procurar_por_id(ot.id_ot)
        self.assertEqual(lida.descricao_avaria, "Avaria de teste")
        self.assertEqual(lida.estado, "Pendente")
        self.assertIsNone(lida.data_saida_real)
        self.assertEqual(lida.custo_total, 0)

    def test_procurar_por_id_inexistente(self):
        self.assertIsNone(self.repo.procurar_por_id(99))

    def test_atualizar(self):
        ot = self._criar()
        ot.estado = OrdemTrabalho.ESTADO_CONCLUIDA
        ot.data_saida_real = "2026-10-29"
        ot.custo_total = 120.5
        self.assertTrue(self.repo.atualizar(ot))
        lida = self.repo.procurar_por_id(ot.id_ot)
        self.assertEqual(lida.estado, "Concluída")
        self.assertEqual(lida.data_saida_real, "2026-10-29")
        self.assertEqual(lida.custo_total, 120.5)

    def test_atualizar_inexistente(self):
        ot = OrdemTrabalho(1, 1, "2026-10-28", "2026-10-30", "x", id_ot=99)
        self.assertFalse(self.repo.atualizar(ot))

    def test_apagar(self):
        ot = self._criar()
        self.assertTrue(self.repo.apagar(ot.id_ot))
        self.assertFalse(self.repo.apagar(ot.id_ot))
        self.assertEqual(self.repo.listar(), [])

    def test_apagar_com_linhas_e_recusado(self):
        ot = self._criar()
        self.linhas.inserir(LinhaOT(ot.id_ot, LinhaOT.TIPO_MAO_OBRA, "x", 1, 10))
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.apagar(ot.id_ot)

    def test_viatura_inexistente_e_recusada(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._criar(id_viatura=99)

    # ----- Alterações pontuais -----

    def test_mudar_estado(self):
        ot = self._criar()
        self.assertTrue(self.repo.mudar_estado(ot.id_ot, OrdemTrabalho.ESTADO_EM_CURSO))
        self.assertEqual(self.repo.procurar_por_id(ot.id_ot).estado, "Em Curso")

    def test_mudar_estado_inexistente(self):
        self.assertFalse(self.repo.mudar_estado(99, OrdemTrabalho.ESTADO_EM_CURSO))

    def test_mudar_estado_invalido(self):
        ot = self._criar()
        with self.assertRaises(ValueError):
            self.repo.mudar_estado(ot.id_ot, "Concluida")
        self.assertEqual(self.repo.procurar_por_id(ot.id_ot).estado, "Pendente")

    def test_atribuir_tecnico(self):
        ot = self._criar()
        self.assertTrue(self.repo.atribuir_tecnico(ot.id_ot, 2))
        self.assertEqual(self.repo.procurar_por_id(ot.id_ot).id_tecnico, 2)

    def test_atribuir_tecnico_inexistente_e_recusado(self):
        ot = self._criar()
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.atribuir_tecnico(ot.id_ot, 77)

    def test_atualizar_custo_total(self):
        ot = self._criar()
        self.assertTrue(self.repo.atualizar_custo_total(ot.id_ot, 55.25))
        self.assertEqual(self.repo.procurar_por_id(ot.id_ot).custo_total, 55.25)
        self.assertFalse(self.repo.atualizar_custo_total(99, 1))

    # ----- Pesquisas -----

    def test_listar_mais_recentes_primeiro(self):
        self._criar(data_entrada="2026-10-05")
        self._criar(data_entrada="2026-10-20")
        self._criar(data_entrada="2026-10-10")
        self.assertEqual(self._ids(self.repo.listar()), [2, 3, 1])

    def test_listar_por_viatura(self):
        self._criar(id_viatura=1, data_entrada="2026-10-05")
        self._criar(id_viatura=2)
        self._criar(id_viatura=1, data_entrada="2026-10-20")
        self.assertEqual(self._ids(self.repo.listar_por_viatura(1)), [3, 1])
        self.assertEqual(self.repo.listar_por_viatura(99), [])

    def test_listar_por_matricula(self):
        self._criar(id_viatura=1, data_entrada="2026-10-05")
        self._criar(id_viatura=2, data_entrada="2026-10-10")
        self._criar(id_viatura=2, data_entrada="2026-10-20")
        self.assertEqual(self._ids(self.repo.listar_por_matricula("CC-22-DD")), [3, 2])
        # não distingue maiúsculas de minúsculas
        self.assertEqual(self._ids(self.repo.listar_por_matricula("aa-11-bb")), [1])
        self.assertEqual(self.repo.listar_por_matricula("ZZ-00-ZZ"), [])

    def test_listar_em_curso(self):
        self._criar(estado=OrdemTrabalho.ESTADO_PENDENTE)
        self._criar(estado=OrdemTrabalho.ESTADO_EM_CURSO, data_entrada="2026-10-01")
        self._criar(estado=OrdemTrabalho.ESTADO_AGUARDA_PECA, data_entrada="2026-10-02")
        self._criar(estado=OrdemTrabalho.ESTADO_CONCLUIDA)
        self._criar(estado=OrdemTrabalho.ESTADO_ENTREGUE)
        self.assertEqual(self._ids(self.repo.listar_em_curso()), [3, 2])

    def test_pesquisar_sem_filtros_devolve_tudo(self):
        self._criar()
        self._criar()
        self.assertEqual(len(self.repo.pesquisar()), 2)

    def test_pesquisar_por_estado(self):
        self._criar()
        self._criar(estado=OrdemTrabalho.ESTADO_ENTREGUE)
        self.assertEqual(self._ids(self.repo.pesquisar(estado="Entregue")), [2])

    def test_pesquisar_por_tecnico(self):
        self._criar(id_tecnico=1)
        self._criar(id_tecnico=2)
        self.assertEqual(self._ids(self.repo.pesquisar(id_tecnico=2)), [2])

    def test_pesquisar_por_datas(self):
        self._criar(data_entrada="2026-10-05")
        self._criar(data_entrada="2026-10-31 14:30")  # com hora
        self._criar(data_entrada="2026-11-03")
        self.assertEqual(
            self._ids(self.repo.pesquisar(data_inicio="2026-10-06", data_fim="2026-10-31")),
            [2])
        self.assertEqual(self._ids(self.repo.pesquisar(data_inicio="2026-11-01")), [3])
        self.assertEqual(self._ids(self.repo.pesquisar(data_fim="2026-10-10")), [1])

    def test_pesquisar_com_filtros_combinados(self):
        self._criar(id_tecnico=1, data_entrada="2026-10-05")
        self._criar(id_tecnico=1, data_entrada="2026-10-20",
                    estado=OrdemTrabalho.ESTADO_EM_CURSO)
        self._criar(id_tecnico=2, data_entrada="2026-10-20",
                    estado=OrdemTrabalho.ESTADO_EM_CURSO)
        resultado = self.repo.pesquisar(data_inicio="2026-10-10", estado="Em Curso",
                                        id_tecnico=1)
        self.assertEqual(self._ids(resultado), [2])
