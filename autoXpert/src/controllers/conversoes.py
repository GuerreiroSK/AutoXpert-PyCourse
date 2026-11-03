def ler_decimal(texto: str, campo: str) -> float:
    """Aceita a virgula decimal usada em Portugal, sem separadores de milhares."""
    try:
        return float(texto.strip().replace(",", "."))
    except ValueError as erro:
        raise ValueError(f"O campo '{campo}' deve ser numerico (exemplo: 12,50).") from erro


def ler_inteiro(texto: str, campo: str) -> int:
    try:
        return int(texto.strip())
    except ValueError as erro:
        raise ValueError(f"O campo '{campo}' deve ser um inteiro (exemplo: 3).") from erro
