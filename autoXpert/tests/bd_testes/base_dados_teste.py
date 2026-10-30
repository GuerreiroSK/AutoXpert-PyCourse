import sqlite3
from pathlib import Path

# O schema real do projeto (db/schema.sql). Os testes usam-no para a base de dados
# de teste ser igual à verdadeira: se o schema mudar, os testes apanham o problema.
# Este ficheiro está em autoXpert/tests/bd_testes/, por isso a raiz do projeto
# (autoXpert/) está 2 níveis acima da pasta onde ele está.
CAMINHO_SCHEMA = Path(__file__).resolve().parents[2] / "db" / "schema.sql"


# Cria uma base de dados SQLite em memória, só para os testes (desaparece no fim),
# com o schema real e alguns registos de que as OTs dependem:
#   2 viaturas (ids 1 e 2), 2 técnicos (ids 1 e 2), 2 peças (ids 1 e 2).
# Nunca toca em db/autoxpert.db.
def criar_conexao_teste():
    conexao = sqlite3.connect(":memory:")
    conexao.row_factory = sqlite3.Row  # igual a db/connection.py
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.executescript(CAMINHO_SCHEMA.read_text(encoding="utf-8"))
    conexao.executescript("""
    INSERT INTO Cliente (nome, NIF) VALUES ('Cliente Teste', '123456789');

    INSERT INTO Viatura (matricula, marca, modelo, id_cliente)
        VALUES ('AA-11-BB', 'Renault', 'Clio', 1);
    INSERT INTO Viatura (matricula, marca, modelo, id_cliente)
        VALUES ('CC-22-DD', 'Opel', 'Corsa', 1);

    INSERT INTO Tecnico (nome, custo_hora) VALUES ('Técnico 1', 25);
    INSERT INTO Tecnico (nome, custo_hora) VALUES ('Técnico 2', 30);

    INSERT INTO Peca (referencia, nome, preco_compra, preco_venda)
        VALUES ('REF-1', 'Pastilhas', 10, 25);
    INSERT INTO Peca (referencia, nome, preco_compra, preco_venda)
        VALUES ('REF-2', 'Filtro', 5, 15);
    """)
    return conexao