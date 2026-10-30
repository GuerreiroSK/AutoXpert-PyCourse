from math import isfinite


def texto_obrigatorio(valor: str, campo: str) -> str:
    texto = valor.strip()
    if not texto:
        raise ValueError(f"O campo '{campo}' e obrigatorio.")
    return texto


def validar_valor(valor: float, campo: str) -> None:
    if not isfinite(valor) or valor < 0:
        raise ValueError(f"O campo '{campo}' deve ser um numero finito, igual ou superior a zero.")


def validar_quantidade(valor: int, campo: str) -> None:
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        raise ValueError(f"O campo '{campo}' deve ser um inteiro igual ou superior a zero.")
