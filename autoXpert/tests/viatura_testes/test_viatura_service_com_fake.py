
import unittest
import sqlite3

from src.services.viatura_service import ViaturaService
from src.models.viatura import Viatura


class FakeViaturaRepository:

    def __init__(self):
        self.viaturas = []
        self.proximo_id = 1

    def criar(self, viatura):
        viatura.id_viatura = self.proximo_id
        self.proximo_id += 1
        self.viaturas.append(viatura)
        return viatura.id_viatura

    def obter_por_id(self, id_viatura):
        for viatura in self.viaturas:
            if viatura.id_viatura == id_viatura:
                return viatura
        return None

    def obter_por_matricula(self, matricula):
        for viatura in self.viaturas:
            if viatura.matricula == matricula:
                return viatura
        return None

    def listar_todas(self):
        return self.viaturas

    def listar_por_cliente(self, id_cliente):
        return [
            v for v in self.viaturas
            if v.id_cliente == id_cliente
        ]

    def atualizar(self, viatura):
        for i, v in enumerate(self.viaturas):
            if v.id_viatura == viatura.id_viatura:
                self.viaturas[i] = viatura
                return True
        return False

    def eliminar(self, id_viatura):
        viatura = self.obter_por_id(id_viatura)

        if viatura:
            self.viaturas.remove(viatura)
            return True

        return False


# Versão anterior: usa um repositório falso feito à mão (FakeViaturaRepository).
# Os testes com MagicMock (estilo da aula) estão em test_viatura_service.py
class TestViaturaServiceComFake(unittest.TestCase):

    def setUp(self):
        self.conexao = sqlite3.connect(":memory:")
        self.conexao.row_factory = sqlite3.Row

        self.conexao.execute("""
            CREATE TABLE Cliente (
                id_cliente INTEGER PRIMARY KEY,
                nome TEXT
            )
        """)

        self.conexao.execute("""
            INSERT INTO Cliente (id_cliente, nome)
            VALUES (1, 'Cliente Teste')
        """)

        self.conexao.commit()

        self.repository = FakeViaturaRepository()

        self.service = ViaturaService(
            self.repository,
            self.conexao
        )

    def tearDown(self):
        self.conexao.close()

    def criar_viatura(self):
        return Viatura(
            matricula="AA-00-BB",
            marca="BMW",
            modelo="Série 1",
            id_cliente=1,
            ano=2022,
            cor="Preto",
            km_estrada=10000
        )

    def test_registar_viatura(self):
        viatura = self.criar_viatura()

        resultado = self.service.registar_viatura(viatura)

        self.assertIsNotNone(resultado)
        self.assertEqual(len(self.repository.viaturas), 1)

    def test_registar_viatura_sem_matricula(self):
        viatura = self.criar_viatura()
        viatura.matricula = ""

        with self.assertRaises(ValueError):
            self.service.registar_viatura(viatura)

    def test_registar_viatura_sem_marca(self):
        viatura = self.criar_viatura()
        viatura.marca = ""

        with self.assertRaises(ValueError):
            self.service.registar_viatura(viatura)

    def test_registar_viatura_sem_modelo(self):
        viatura = self.criar_viatura()
        viatura.modelo = ""

        with self.assertRaises(ValueError):
            self.service.registar_viatura(viatura)

    def test_registar_viatura_cliente_inexistente(self):
        viatura = self.criar_viatura()
        viatura.id_cliente = 99

        with self.assertRaises(ValueError):
            self.service.registar_viatura(viatura)

    def test_registar_viatura_matricula_duplicada(self):
        viatura = self.criar_viatura()
        self.service.registar_viatura(viatura)

        segunda = self.criar_viatura()

        with self.assertRaises(ValueError):
            self.service.registar_viatura(segunda)

    def test_registar_viatura_km_negativos(self):
        viatura = self.criar_viatura()
        viatura.km_estrada = -100

        with self.assertRaises(ValueError):
            self.service.registar_viatura(viatura)

    def test_consultar_viatura_por_id(self):
        viatura = self.criar_viatura()
        self.service.registar_viatura(viatura)

        resultado = self.service.consultar_por_id(1)

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.matricula, "AA-00-BB")

    def test_consultar_viatura_inexistente(self):
        # O service lança ValueError quando a viatura não existe
        with self.assertRaises(ValueError):
            self.service.consultar_por_id(99)

    def test_consultar_por_matricula(self):
        viatura = self.criar_viatura()
        self.service.registar_viatura(viatura)

        resultado = self.service.consultar_por_matricula("AA-00-BB")

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.marca, "BMW")

    def test_listar_viaturas(self):
        self.service.registar_viatura(self.criar_viatura())

        resultado = self.service.listar_viaturas()

        self.assertEqual(len(resultado), 1)

    def test_atualizar_viatura(self):
        viatura = self.criar_viatura()
        self.service.registar_viatura(viatura)

        viatura.marca = "Mercedes"

        resultado = self.service.atualizar_viatura(viatura)

        self.assertTrue(resultado)

    def test_eliminar_viatura(self):
        viatura = self.criar_viatura()
        self.service.registar_viatura(viatura)

        resultado = self.service.eliminar_viatura(1)

        self.assertTrue(resultado)


if __name__ == "__main__":
    unittest.main()
