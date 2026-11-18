import unittest

from src.services.validacao import validar_campos, validar_numero_telefone


class TestValidarCampos(unittest.TestCase):

    def test_campos_obrigatorios_vazios(self):
        erros = validar_campos({"Nome": "", "Email": "teste@exemplo.pt"})

        self.assertEqual(erros, ["Nome é obrigatório."])

    def test_so_espacos_conta_como_vazio(self):
        self.assertEqual(validar_campos({"Nome": "   "}), ["Nome é obrigatório."])

    def test_valor_none_conta_como_vazio(self):
        self.assertEqual(validar_campos({"Nome": None}), ["Nome é obrigatório."])

    def test_devolve_todos_os_erros_de_uma_vez(self):
        erros = validar_campos({"Nome": "", "Morada": ""})

        self.assertEqual(len(erros), 2)

    def test_campos_numericos_validos(self):
        erros = validar_campos({
            "NIF": {"valor": "123456789", "tipo": "inteiro"},
            "Preço": {"valor": "12,50", "tipo": "decimal"},
        })

        self.assertEqual(erros, [])

    def test_campos_numericos_invalidos(self):
        erros = validar_campos({
            "NIF": {"valor": "12A", "tipo": "inteiro"},
            "Preço": {"valor": "abc", "tipo": "decimal"},
        })

        self.assertEqual(len(erros), 2)

    def test_decimal_nao_aceita_infinito_nem_nan(self):
        for valor in ("inf", "nan", "-inf"):
            erros = validar_campos({"Preço": {"valor": valor, "tipo": "decimal"}})
            self.assertEqual(len(erros), 1, valor)

    def test_campo_opcional_vazio(self):
        self.assertEqual(validar_campos({"Telefone": {"valor": "", "obrigatorio": False}}), [])

    def test_campo_opcional_preenchido_e_validado(self):
        erros = validar_campos({"Ano": {"valor": "abc", "obrigatorio": False, "tipo": "inteiro"}})

        self.assertEqual(len(erros), 1)

    def test_telefone(self):
        self.assertIsNone(validar_numero_telefone("912345678"))
        self.assertIsNone(validar_numero_telefone("+351 912-345-678"))
        self.assertIsNone(validar_numero_telefone(""))
        self.assertIsNotNone(validar_numero_telefone("telefone"))


if __name__ == "__main__":
    unittest.main()
