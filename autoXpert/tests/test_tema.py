"""Torna tests/test_tema.py independente da fonte instalada na máquina.

Porquê: o teste compara a fonte que o Tk desenhou com a string "Calibri".
Só passa onde a Calibri existe (Windows/Office). Noutros sistemas o Tk
escolhe uma parecida (ex.: "Noto Sans") e o teste falha, embora a aplicação
esteja certa. A correção compara com o que o Tk devolve para "Calibri" NESTA
máquina, por isso passa em qualquer sistema e continua a apanhar erros reais
(ex.: alguém trocar a FONTE no tema).

Uso (na pasta autoXpert):  python3 corrigir_test_tema.py
"""
import re
import sys
from pathlib import Path

caminho = Path(sys.argv[1] if len(sys.argv) > 1 else "tests/test_tema.py")
texto = caminho.read_text(encoding="utf-8")

if "fonte_esperada" in texto:
    print("Já está corrigido, nada a fazer.")
    sys.exit(0)

ajuda = '''

def fonte_esperada(familia="Calibri"):
    """Família que o Tk realmente usa para `familia` NESTA máquina.

    Se a Calibri existir devolve "Calibri"; se não existir devolve a
    substituta que o Tk escolher (Noto Sans, DejaVu Sans, ...). Assim o teste
    verifica que o tema pede a fonte certa sem depender do sistema operativo.
    """
    import tkinter
    from tkinter import font as tkfont
    raiz = tkinter.Tk()
    raiz.withdraw()
    try:
        return tkfont.Font(root=raiz, family=familia).actual("family")
    finally:
        raiz.destroy()
'''

# 1) trocar o literal "Calibri" nas linhas de verificação (assert...)
linhas = texto.split("\n")
trocas = 0
for i, linha in enumerate(linhas):
    if "assert" in linha and re.search(r"""["']Calibri["']""", linha):
        linhas[i] = re.sub(r"""["']Calibri["']""", "fonte_esperada()", linha)
        trocas += 1
        print(f"linha {i + 1}: {linhas[i].strip()}")

if trocas == 0:
    print("Não encontrei nenhuma linha assert com \"Calibri\". Cola-me o resultado de:")
    print('   grep -n "Calibri" tests/test_tema.py')
    sys.exit(1)

texto = "\n".join(linhas)

# 2) inserir a função auxiliar a seguir aos imports do topo
ultimo_import = 0
for i, linha in enumerate(texto.split("\n")):
    if re.match(r"(import|from)\s", linha):
        ultimo_import = i
partes = texto.split("\n")
partes.insert(ultimo_import + 1, ajuda.rstrip("\n"))
caminho.write_text("\n".join(partes), encoding="utf-8")
print(f"\nFeito: {trocas} verificação(ões) corrigida(s) em {caminho}.")