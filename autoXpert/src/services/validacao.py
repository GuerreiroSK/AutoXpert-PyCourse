from math import isfinite


# Devolve o texto sem espaços nas pontas; levanta erro se ficar vazio
def texto_obrigatorio(valor, campo):
    texto = valor.strip()
    if texto == "":
        raise ValueError("O campo '" + campo + "' é obrigatório.")
    return texto


# O valor (preço, custo...) tem de ser um número normal, igual ou superior a zero
def validar_valor(valor, campo):
    if not isfinite(valor) or valor < 0:
        raise ValueError("O campo '" + campo
                         + "' deve ser um número igual ou superior a zero.")


# A quantidade tem de ser um número inteiro, igual ou superior a zero
def validar_quantidade(valor, campo):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        raise ValueError("O campo '" + campo
                         + "' deve ser um inteiro igual ou superior a zero.")
