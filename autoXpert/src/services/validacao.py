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


def validar_campos(campos_dict):
    """Valida campos obrigatórios e tipos numéricos.

    Formato aceite: {"Nome": valor} ou
    {"Nome": {"valor": valor, "obrigatorio": True, "tipo": "inteiro"|"decimal"}}.
    Devolve sempre uma lista de mensagens; não lança exceções.
    """
    erros = []
    for nome, configuracao in campos_dict.items():
        if isinstance(configuracao, dict):
            valor = configuracao.get("valor", "")
            obrigatorio = configuracao.get("obrigatorio", True)
            tipo = configuracao.get("tipo")
        else:
            valor, obrigatorio, tipo = configuracao, True, None

        texto = "" if valor is None else str(valor).strip()
        if obrigatorio and not texto:
            erros.append(str(nome) + " é obrigatório.")
            continue
        if not texto:
            continue

        if tipo == "inteiro" and not texto.isdigit():
            erros.append(str(nome) + " deve conter apenas números inteiros.")
        elif tipo == "decimal":
            try:
                numero = float(texto.replace(",", "."))
                if not isfinite(numero):
                    raise ValueError
            except (TypeError, ValueError):
                erros.append(str(nome) + " deve ser um número válido.")
    return erros


def validar_numero_telefone(valor, campo="Telefone"):
    """Valida telefone numérico, permitindo o prefixo + e espaços/hífens."""
    texto = "" if valor is None else str(valor).strip()
    if texto and not texto.replace("+", "", 1).replace(" ", "").replace("-", "").isdigit():
        return campo + " deve conter apenas números (pode incluir + e hífen)."
    return None
