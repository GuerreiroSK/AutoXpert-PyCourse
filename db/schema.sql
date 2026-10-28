
CREATE TABLE IF NOT EXISTS Cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    NIF TEXT UNIQUE,
    telefone TEXT CHECK(telefone IS NULL OR length(telefone) <= 20),
    email TEXT,
    morada TEXT,
    data_registo TEXT NOT NULL DEFAULT (date('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Tecnico (
    id_tecnico INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    especialidade TEXT,
    custo_hora REAL NOT NULL CHECK(custo_hora >= 0),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK(ativo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS Viatura (
    id_viatura INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula TEXT NOT NULL UNIQUE,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    ano INTEGER,
    cor TEXT,
    km_estrada INTEGER NOT NULL DEFAULT 0 CHECK(km_estrada >= 0),
    id_cliente INTEGER NOT NULL REFERENCES Cliente(id_cliente)
);

CREATE TABLE IF NOT EXISTS Peca (
    id_peca INTEGER PRIMARY KEY AUTOINCREMENT,
    referencia TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    stock_atual INTEGER NOT NULL DEFAULT 0 CHECK(stock_atual >= 0),
    stock_minimo INTEGER NOT NULL DEFAULT 0 CHECK(stock_minimo >= 0),
    preco_compra REAL NOT NULL CHECK(preco_compra >= 0),
    preco_venda REAL NOT NULL CHECK(preco_venda >= 0),
    fornecedor TEXT
);

CREATE TABLE IF NOT EXISTS OrdemTrabalho (
    id_ot INTEGER PRIMARY KEY AUTOINCREMENT,
    id_viatura INTEGER NOT NULL REFERENCES Viatura(id_viatura),
    id_tecnico INTEGER NOT NULL REFERENCES Tecnico(id_tecnico),
    data_entrada TEXT NOT NULL,
    data_prev_saida TEXT NOT NULL,
    data_saida_real TEXT,
    estado TEXT NOT NULL,
    descricao_avaria TEXT NOT NULL,
    custo_total REAL NOT NULL DEFAULT 0 CHECK(custo_total >= 0)
);

CREATE TABLE IF NOT EXISTS LinhaOT (
    id_linha INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ot INTEGER NOT NULL REFERENCES OrdemTrabalho(id_ot),
    tipo TEXT NOT NULL CHECK(tipo IN ('mao_obra', 'peca')),
    descricao TEXT NOT NULL,
    quantidade REAL NOT NULL CHECK(quantidade > 0),
    horas_trabalhadas REAL,
    preco_unitario REAL NOT NULL CHECK(preco_unitario >= 0),
    id_peca INTEGER REFERENCES Peca(id_peca)
);

CREATE TABLE IF NOT EXISTS Fatura (
    id_fatura INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ot INTEGER NOT NULL UNIQUE REFERENCES OrdemTrabalho(id_ot),
    data_emissao TEXT NOT NULL,
    valor_total REAL NOT NULL CHECK(valor_total >= 0),
    pago INTEGER NOT NULL DEFAULT 0 CHECK(pago IN (0, 1)),
    data_pagamento TEXT,
    metodo_pagamento TEXT
);

CREATE TABLE IF NOT EXISTS LogAlteracaoOT (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ot INTEGER NOT NULL REFERENCES OrdemTrabalho(id_ot),
    data_hora TEXT NOT NULL,
    campo_alterado TEXT NOT NULL,
    valor_anterior TEXT,
    valor_novo TEXT
);
