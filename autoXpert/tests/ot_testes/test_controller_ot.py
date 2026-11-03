import unittest
from datetime import date

from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.services.ot_service import OrdemTrabalhoService
from src.controllers.ot_controller import OrdemTrabalhoController
from tests.bd_testes.base_dados_teste import criar_conexao_teste


class TesteOrdemTrabalhoController(unittest.TestCase):
    # O controller recebe texto (como vem da janela) e devolve sempre (ok, resultado).

    def setUp(self):
        self.conexao = criar_conexao_teste()
        service = OrdemTrabalhoService(OrdemTrabalhoRepository(self.conexao))
        self.controller = OrdemTrabalhoController(service)

    def tearDown(self):
        self.conexao.close()

    # Cria uma OT com texto, como se viesse da janela
    def _criar(self, id_viatura="1", id_tecnico="1", entrada="2026-10-28",
               prevista="2026-10-30", descricao="Travões a chiar"):
        return self.controller.criar_ot(id_viatura, id_tecnico, entrada, prevista, descricao)

    def _ids(self, resultado):
        ok, ots = resultado
        self.assertTrue(ok)
        ids = []
        for ot in ots:
            ids.append(ot.id_ot)
        return ids

    def test_lista_de_estados(self):
        self.assertEqual(self.controller.lista_estados(),
                         ["Pendente", "Em Curso", "Aguarda Peça", "Concluída", "Entregue"])

    def test_criar_ot_com_texto_da_janela(self):
        ok, ot = self._criar(id_viatura=" 1 ", id_tecnico="2")
        self.assertTrue(ok)
        self.assertEqual(ot.id_ot, 1)
        self.assertEqual(ot.id_viatura, 1)
        self.assertEqual(ot.id_tecnico, 2)
        self.assertEqual(ot.estado, "Pendente")

    def test_criar_ot_com_ids_que_nao_sao_numeros(self):
        self.assertEqual(self._criar(id_viatura="abc"),
                         (False, "A viatura tem de ser um número inteiro"))
        self.assertEqual(self._criar(id_tecnico="1.5"),
                         (False, "O técnico tem de ser um número inteiro"))

    def test_criar_ot_sem_tecnico_ou_sem_viatura(self):
        self.assertEqual(self._criar(id_tecnico=""),
                         (False, "A OT tem de ter um técnico responsável"))
        self.assertEqual(self._criar(id_viatura="  "),
                         (False, "Tem de indicar a viatura"))

    def test_criar_ot_com_dados_invalidos(self):
        ok, mensagem = self._criar(entrada="28/10/2026")
        self.assertFalse(ok)
        self.assertIn("AAAA-MM-DD", mensagem)
        ok, mensagem = self._criar(entrada="2026-10-30", prevista="2026-10-28")
        self.assertFalse(ok)
        ok, mensagem = self._criar(descricao="   ")
        self.assertEqual((ok, mensagem), (False, "A descrição da avaria é obrigatória"))

    def test_criar_ot_com_viatura_ou_tecnico_inexistente(self):
        mensagem = "A viatura ou o técnico indicados não existem"
        self.assertEqual(self._criar(id_viatura="99"), (False, mensagem))
        self.assertEqual(self._criar(id_tecnico="99"), (False, mensagem))

    def test_obter_ot(self):
        self._criar()
        ok, ot = self.controller.obter_ot(1)
        self.assertTrue(ok)
        self.assertEqual(ot.descricao_avaria, "Travões a chiar")
        self.assertEqual(self.controller.obter_ot(99), (False, "OT não encontrada: 99"))

    def test_mudar_estado(self):
        self._criar()
        ok, ot = self.controller.mudar_estado(1, "Em Curso")
        self.assertTrue(ok)
        self.assertEqual(ot.estado, "Em Curso")

    def test_mudar_estado_invalido(self):
        self._criar()
        self.assertEqual(self.controller.mudar_estado(1, "Concluida"),
                         (False, "Estado inválido: Concluida"))
        self.assertEqual(self.controller.mudar_estado(99, "Em Curso"),
                         (False, "OT não encontrada: 99"))

    def test_so_se_entrega_uma_ot_concluida(self):
        self._criar()
        ok, mensagem = self.controller.mudar_estado(1, "Entregue")
        self.assertFalse(ok)
        self.assertIn("Concluída", mensagem)

    def test_entregar_com_data_vazia_usa_a_data_de_hoje(self):
        self._criar(entrada="2026-01-01", prevista="2026-01-05")
        self.controller.mudar_estado(1, "Concluída")
        ok, ot = self.controller.mudar_estado(1, "Entregue", "")
        self.assertTrue(ok)
        self.assertEqual(ot.data_saida_real, date.today().isoformat())

    def test_entregar_com_data_indicada(self):
        self._criar()
        self.controller.mudar_estado(1, "Concluída")
        ok, ot = self.controller.mudar_estado(1, "Entregue", " 2026-10-31 ")
        self.assertTrue(ok)
        self.assertEqual(ot.data_saida_real, "2026-10-31")

    def test_atribuir_tecnico(self):
        self._criar()
        ok, ot = self.controller.atribuir_tecnico(1, "2")
        self.assertTrue(ok)
        self.assertEqual(ot.id_tecnico, 2)

    def test_atribuir_tecnico_casos_invalidos(self):
        self._criar()
        self.assertEqual(self.controller.atribuir_tecnico(1, "x"),
                         (False, "O técnico tem de ser um número inteiro"))
        self.assertEqual(self.controller.atribuir_tecnico(1, ""),
                         (False, "Tem de indicar o técnico responsável"))
        self.assertEqual(self.controller.atribuir_tecnico(1, "77"),
                         (False, "A viatura ou o técnico indicados não existem"))

    def test_listar_todas_e_em_curso(self):
        self._criar(entrada="2026-10-01", prevista="2026-10-10")
        self._criar(entrada="2026-10-02", prevista="2026-10-10")
        self._criar(entrada="2026-10-03", prevista="2026-10-10")
        self.controller.mudar_estado(1, "Em Curso")
        self.controller.mudar_estado(2, "Aguarda Peça")
        self.assertEqual(self._ids(self.controller.listar_todas()), [3, 2, 1])
        self.assertEqual(self._ids(self.controller.listar_em_curso()), [2, 1])

    def test_historico_por_matricula(self):
        self._criar(id_viatura="1")
        self._criar(id_viatura="2")
        self.assertEqual(self._ids(self.controller.historico_por_matricula("aa-11-bb")), [1])
        self.assertEqual(self._ids(self.controller.historico_por_matricula("ZZ-00-ZZ")), [])
        self.assertEqual(self.controller.historico_por_matricula("  "),
                         (False, "Tem de indicar a matrícula"))

    def test_pesquisar_ignora_campos_vazios(self):
        self._criar(id_tecnico="1", entrada="2026-10-05", prevista="2026-10-10")
        self._criar(id_tecnico="2", entrada="2026-10-20", prevista="2026-10-25")
        self.controller.mudar_estado(2, "Em Curso")
        self.assertEqual(self._ids(self.controller.pesquisar("", "", "", "")), [2, 1])
        self.assertEqual(self._ids(self.controller.pesquisar(estado="Em Curso")), [2])
        self.assertEqual(self._ids(self.controller.pesquisar(id_tecnico="1")), [1])
        self.assertEqual(self._ids(self.controller.pesquisar("2026-10-01", "2026-10-10")), [1])

    def test_pesquisar_com_filtros_invalidos(self):
        self.assertEqual(self.controller.pesquisar(id_tecnico="abc"),
                         (False, "O técnico tem de ser um número inteiro"))
        ok, mensagem = self.controller.pesquisar(data_inicio="05/10/2026")
        self.assertFalse(ok)
        self.assertIn("AAAA-MM-DD", mensagem)
        ok, mensagem = self.controller.pesquisar("2026-10-20", "2026-10-10")
        self.assertFalse(ok)

    def test_erro_inesperado_da_base_de_dados_vira_mensagem(self):
        self.conexao.close()  # simula uma base de dados indisponível
        ok, mensagem = self.controller.listar_todas()
        self.assertFalse(ok)
        self.assertTrue(mensagem.startswith("Erro na base de dados: "))
