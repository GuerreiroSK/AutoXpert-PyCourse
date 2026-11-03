# Converte o texto escrito nos formulários em números.

# Aceita a vírgula decimal usada em Portugal (ex.: 12,50)
def ler_decimal(texto, campo):
    try:
        return float(texto.strip().replace(",", "."))
    except ValueError:
        raise ValueError("O campo '" + campo + "' deve ser numérico (exemplo: 12,50).")


def ler_inteiro(texto, campo):
    try:
        return int(texto.strip())
    except ValueError:
        raise ValueError("O campo '" + campo + "' deve ser um inteiro (exemplo: 3).")
