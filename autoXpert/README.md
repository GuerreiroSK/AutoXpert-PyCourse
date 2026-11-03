# AutoXpert 🚗🔧

Aplicação de gestão de uma oficina automóvel, feita em **Python** no projeto de grupo do curso IEFP (UFCD 10790, Grupo 2).

É um programa de **ambiente de trabalho** (janelas Tkinter) com os dados guardados numa base de dados **SQLite**.

## O que faz

| Módulo | O que permite |
|---|---|
| Clientes | registar, editar, eliminar e listar clientes |
| Viaturas | registar, procurar por matrícula, atualizar, eliminar e ver o histórico de OTs |
| Técnicos | registar, editar, eliminar e listar (com filtro "apenas ativos") |
| Peças | catálogo, stock, receção de material, ajuste de stock e alerta de stock baixo |
| Ordens de trabalho (OT) | criar OT, atribuir técnico, mudar de estado, linhas de mão de obra e de peças, custo total, pesquisas |
| Faturação | gerar fatura a partir de uma OT, marcar como paga, relatório mensal em Excel |
| Registo de alterações | consultar as alterações às OTs (o estado e o técnico ficam gravados automaticamente) |

## Como correr

### 1. Requisitos

- **Python 3.12** ou superior
- **Tkinter** (as janelas) e **openpyxl** (o relatório em Excel)

No Ubuntu/Debian:

```bash
sudo apt install python3-tk python3-openpyxl
```

Noutros sistemas, o Tkinter já vem com o Python; o `openpyxl` instala-se com `pip install -r requirements.txt`.

### 2. Arrancar

Abrir um terminal **dentro da pasta `autoXpert/`** (a que tem o `main.py`) e correr:

```bash
python3 main.py
```

Abre o **menu principal**, com um botão por módulo. A base de dados (`db/autoxpert.db`) é criada sozinha na primeira vez, a partir de `db/schema.sql`. Para começar do zero, basta apagar esse ficheiro. **Se o schema mudar** (como aconteceu com `km_entrada`), apagar o `autoxpert.db` antigo para ser criado outra vez.

### 3. Primeiro uso (ordem recomendada)

Os dados dependem uns dos outros, por isso o caminho natural é:

1. **Clientes** → registar um cliente.
2. **Viaturas** → registar uma viatura (o cliente escolhe-se numa lista).
3. **Técnicos** → registar pelo menos um técnico (toda a OT tem técnico).
4. **Peças** → registar peças (para as linhas de tipo peça).
5. **Ordens de trabalho** → criar a OT, juntar linhas e ir mudando o estado.
6. **Faturação** → gerar a fatura da OT e marcá-la como paga.

O relatório mensal fica gravado em `docs/Faturacao_AAAA_MM.xlsx`.

## Regras das ordens de trabalho

- Cada OT tem de ter **viatura** e **técnico** que existam.
- Estados: `Pendente`, `Em Curso`, `Aguarda Peça`, `Concluída` e `Entregue`.
- Só se pode **entregar** uma OT que esteja `Concluída`; uma OT entregue já não pode ser alterada.
- O **custo total** é recalculado sempre que se junta ou remove uma linha.
- Linhas `mao_obra` não têm peça; linhas `peca` têm de indicar a peça.
- Cada OT só pode ter **uma fatura**, e só se fatura uma OT que tenha linhas.

## Como o código está organizado

O programa está dividido em camadas. Cada camada só fala com a seguinte:

```
view  →  controller  →  service  →  repository  →  SQLite
```

| Camada | Responsabilidade |
|---|---|
| **model** | classes com os dados (`Cliente`, `Viatura`, `OrdemTrabalho`, ...) |
| **view** | desenha as janelas e recolhe o que o utilizador escreve (sem SQL, sem regras) |
| **controller** | converte o texto das janelas nos tipos certos e chama o service |
| **service** | regras de negócio e validações |
| **repository** | **único** sítio com SQL; recebe a ligação à base de dados no construtor |

```
autoXpert/
├── main.py              # liga todas as camadas e abre o menu principal
├── requirements.txt     # bibliotecas externas (openpyxl)
├── db/
│   ├── connection.py    # get_connection() e inicializar_bd()
│   └── schema.sql       # tabelas
├── docs/                # relatórios Excel gerados
├── src/
│   ├── models/          # <entidade>_model.py
│   ├── repositories/    # <entidade>_repository.py
│   ├── services/        # <entidade>_service.py (+ validacao.py)
│   ├── controllers/     # <entidade>_controller.py (+ conversoes.py)
│   └── views/           # <entidade>_view.py (+ estilo.py: aspeto e avisos comuns)
└── tests/
    ├── cliente_testes/  ├── viatura_testes/  ├── tecnico_testes/  ├── peca_testes/
    ├── ot_testes/       ├── linha_ot_testes/ ├── fatura_testes/   ├── log_alteracao_testes/
    └── bd_testes/       # base de dados em memória usada nos testes
```

### Convenções do grupo

- **Nomes de ficheiros:** `<entidade>_<camada>.py`, por exemplo `peca_service.py`. As entidades são `cliente`, `viatura`, `tecnico`, `peca`, `ot`, `linha_ot`, `fatura` e `log_alteracao_ot`.
- **Repositórios:** todos são classes que recebem a `conexao` no construtor e devolvem objetos do model. Métodos com os mesmos nomes em todos: `inserir`, `obter_por_id`, `listar_todos`, `atualizar` e `eliminar` (mais os específicos de cada um, como `listar_por_ot`).
- **Erros nas views:** as regras levantam `ValueError`; a view mostra-os sempre através de `estilo.py` (uma caixa de aviso), nunca com `messagebox` diretamente.
- **Código:** só o que demos no curso (sem `lambda`, `dataclass`, anotações de tipos, `*args`...).

## Testes

Na pasta `autoXpert/`:

```bash
python3 -m unittest discover -v
```

- Os testes ficam em `tests/<entidade>_testes/`, com o nome `test_<entidade>_<camada>.py`.
- **services:** repositório simulado com `MagicMock` (sem base de dados).
- **repositories e `*_integracao`:** base de dados SQLite em memória, criada a partir de `db/schema.sql` (nunca tocam em `autoxpert.db`).
- Os testes das **views** abrem janelas reais, por isso precisam de ecrã. Num computador normal funciona; num servidor sem ecrã usar `xvfb-run -a python3 -m unittest discover`.

## Trabalho em grupo (Git)

- Cada pessoa trabalha no seu branch (`feature/...`) e junta à `main` por **Pull Request**.
- Antes de começar: `git fetch origin` e `git merge origin/main` para trazer o trabalho dos colegas.
- Antes de fazer commit, correr os testes.
- O `.gitignore` já ignora `__pycache__/`, `*.db` e os relatórios Excel: não fazer commit disso.
