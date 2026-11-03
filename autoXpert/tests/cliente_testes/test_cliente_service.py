
import unittest
from unittest.mock import MagicMock

from src.services.cliente_service import ClienteService
from src.models.cliente_models import Cliente


class TestClienteService(unittest.TestCase):

    def setUp(self):
        # Criar um Repository simulado para não utilizar a base de dados
        self.mock_repo = MagicMock()
        self.svc = ClienteService(self.mock_repo)

    # CREATE - Registar cliente

    def test_registar_cliente_com_nome_vazio_levanta_erro(self):
        # Verificar se o nome vazio é rejeitado
        with self.assertRaises(ValueError):
            self.svc.registar("", "123456789", "912345678",
                              "teste@email.com", "Lisboa")

        # Confirmar que não foi feita nenhuma inserção
        self.mock_repo.inserir.assert_not_called()

    def test_registar_cliente_com_nome_apenas_espacos_levanta_erro(self):
        # Um nome composto apenas por espaços também é inválido
        with self.assertRaises(ValueError):
            self.svc.registar("   ", "123456789", None, None, None)

        self.mock_repo.inserir.assert_not_called()

    def test_registar_cliente_com_telefone_demasiado_longo_levanta_erro(self):
        # O telefone não pode ultrapassar 20 caracteres
        with self.assertRaises(ValueError):
            self.svc.registar("João", "123456789",
                              "123456789012345678901", None, None)

        self.mock_repo.inserir.assert_not_called()

    def test_registar_cliente_com_dados_validos(self):
        # Registar um cliente com dados válidos
        self.svc.registar("João Silva", "123456789", "912345678",
                          "teste@email.com", "Lisboa")

        self.mock_repo.inserir.assert_called_once()

        # Obter o objeto Cliente enviado ao Repository
        cliente = self.mock_repo.inserir.call_args[0][0]

        # Confirmar que os dados foram corretamente preenchidos
        self.assertEqual(cliente.nome, "João Silva")
        self.assertEqual(cliente.nif, "123456789")
        self.assertEqual(cliente.telefone, "912345678")

    def test_registar_cliente_remove_espacos_do_nome(self):
        # Confirmar que os espaços no início e no fim são removidos
        self.svc.registar("  João Silva  ", None, None, None, None)

        cliente = self.mock_repo.inserir.call_args[0][0]

        self.assertEqual(cliente.nome, "João Silva")

    def test_registar_cliente_com_campos_opcionais_vazios(self):
        # Campos opcionais vazios devem ser guardados como None
        self.svc.registar("João Silva", "", "", "", "")

        cliente = self.mock_repo.inserir.call_args[0][0]

        self.assertIsNone(cliente.nif)
        self.assertIsNone(cliente.telefone)
        self.assertIsNone(cliente.email)
        self.assertIsNone(cliente.morada)

    # READ - Listar clientes

    def test_listar_devolve_lista_do_repo(self):
        # Simular uma lista de clientes devolvida pelo Repository
        lista = [
            Cliente(
                nome="João", nif="123456789", telefone=None,
                email=None, morada=None, data_registo="2026-11-03",
                id_cliente=1
            ),
            Cliente(
                nome="Maria", nif="987654321", telefone=None,
                email=None, morada=None, data_registo="2026-11-03",
                id_cliente=2
            )
        ]

        self.mock_repo.listar_todos.return_value = lista

        resultado = self.svc.listar_todos()

        # Confirmar que os dois clientes foram devolvidos
        self.assertEqual(len(resultado), 2)
        self.mock_repo.listar_todos.assert_called_once()

    # READ - Consultar cliente por ID

    def test_obter_cliente_existente(self):
        # Simular a existência de um cliente com ID 1
        cliente = Cliente(
            nome="João", nif="123456789", telefone=None,
            email=None, morada=None, data_registo="2026-11-03",
            id_cliente=1
        )

        self.mock_repo.obter_por_id.return_value = cliente

        resultado = self.svc.obter_por_id(1)

        # Confirmar que o cliente correto foi devolvido
        self.assertEqual(resultado.nome, "João")
        self.mock_repo.obter_por_id.assert_called_once_with(1)

    def test_obter_cliente_inexistente_levanta_erro(self):
        # Simular um ID que não corresponde a nenhum cliente
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.obter_por_id(999)

    # UPDATE - Atualizar cliente

    def test_atualizar_cliente_com_nome_vazio_levanta_erro(self):
        # Não permitir a atualização de um cliente sem nome
        cliente = Cliente(
            nome="", nif="123456789", telefone=None,
            email=None, morada=None, data_registo="2026-11-03",
            id_cliente=1
        )

        with self.assertRaises(ValueError):
            self.svc.atualizar(cliente)

        self.mock_repo.atualizar.assert_not_called()

    def test_atualizar_cliente_inexistente_levanta_erro(self):
        # Simular que o cliente não existe no Repository
        cliente = Cliente(
            nome="João", nif="123456789", telefone=None,
            email=None, morada=None, data_registo="2026-11-03",
            id_cliente=999
        )

        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.atualizar(cliente)

        self.mock_repo.atualizar.assert_not_called()

    def test_atualizar_cliente_existente(self):
        # Simular que o cliente existe e pode ser atualizado
        cliente = Cliente(
            nome="João Silva", nif="123456789", telefone="912345678",
            email=None, morada=None, data_registo="2026-11-03",
            id_cliente=1
        )

        self.mock_repo.obter_por_id.return_value = cliente

        self.svc.atualizar(cliente)

        self.mock_repo.atualizar.assert_called_once_with(cliente)

    # DELETE - Eliminar cliente

    def test_eliminar_cliente_existente(self):
        # Simular que o cliente existe antes de o eliminar
        cliente = Cliente(
            nome="João", nif="123456789", telefone=None,
            email=None, morada=None, data_registo="2026-11-03",
            id_cliente=1
        )

        self.mock_repo.obter_por_id.return_value = cliente

        self.svc.eliminar(1)

        self.mock_repo.eliminar.assert_called_once_with(1)

    def test_eliminar_cliente_inexistente_levanta_erro(self):
        # Não permitir a eliminação de um cliente inexistente
        self.mock_repo.obter_por_id.return_value = None

        with self.assertRaises(ValueError):
            self.svc.eliminar(999)

        self.mock_repo.eliminar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
