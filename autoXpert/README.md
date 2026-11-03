# AutoXpert

Sistema de gestão de oficina automóvel, desenvolvido em Python no projeto de grupo do curso IEFP (UFCD 10790, Grupo 2).

Aplicação de **ambiente de trabalho (Tkinter)** com base de dados **SQLite**, organizada em camadas (MVC):

```
view  →  controller  →  service  →  repository  →  SQLite
```

- **view:** desenha as janelas e recolhe o que o utilizador escreve. Não tem SQL nem regras.
- **controller:** converte o texto das janelas nos tipos certos e chama o service.
- **service:** regras de negócio e validações.
- **repository:** único sítio com SQL.

## Módulos

| Módulo | O que permite |
|---|---|
| Clientes | registar, editar, eliminar e listar clientes |
| Viaturas | registar, consultar por matrícula, listar, atualizar, eliminar e ver o histórico de OTs |
| Técnicos | registar, editar, eliminar, listar (filtro "apenas ativos") |
| Peças | catálogo, stock, receção de material, ajuste de stock e alerta de stock baixo |
| Ordens de trabalho | criar OT, atribuir técnico, mudar de estado, linhas de mão de obra e peças, custo total, pesquisa por matrícula, estado, técnico e datas |
| Faturação | gerar fatura a partir de uma OT, fatura manual, marcar como paga, eliminar, relatório mensal em Excel |
| Registo de alterações | registar e consultar as alterações feitas às OTs |

## Como correr

Requisitos: **Python 3.12** (ou superior) com Tkinter e a biblioteca `openpyxl` (usada no relatório de faturação).

No Ubuntu/Debian:

```bash
sudo apt install python3-tk python3-openpyxl
```

Arrancar a aplicação, a partir da pasta `autoXpert/`:

```bash
python3 main.py
```

Abre o **menu principal**, com um botão por módulo. A base de dados (`db/autoxpert.db`) é criada automaticamente na primeira execução, a partir de `db/schema.sql`.

Para abrir só a janela das ordens de trabalho: `python3 abrir_ots.py`.

### Ordem recomendada para um primeiro uso

Há dependências entre os dados, por isso o caminho natural é:

1. **Clientes** → registar um cliente.
2. **Viaturas** → registar uma viatura (escolhe-se o cliente numa lista).
3. **Técnicos** → registar pelo menos um técnico (a OT exige técnico).
4. **Peças** → registar peças (necessárias nas linhas de tipo peça).
5. **Ordens de trabalho** → criar a OT, adicionar linhas e ir mudando o estado.
6. **Faturação** → gerar a fatura da OT (precisa de ter linhas) e marcá-la como paga.

O relatório mensal em Excel é gravado em `docs/Faturacao_AAAA_MM.xlsx`.

## Testes

A partir da pasta `autoXpert/`:

```bash
python3 -m unittest discover -v
```

Os testes das **views** abrem janelas reais, por isso precisam de ambiente gráfico (num servidor sem ecrã usar `xvfb-run -a python3 -m unittest discover`).

Tipos de testes:
- **services:** com `MagicMock` (sem base de dados), um ficheiro por service.
- **integração** (`*_integracao_*`): service + repositório sobre uma base de dados SQLite em memória, criada a partir de `db/schema.sql`.
- **repositórios, modelos e controllers:** cada módulo na sua pasta `tests/<módulo>_testes/`. Os de técnicos e peças estão em `tests_tecnicos_pecas/`.

## Estrutura

```
autoXpert/
├── main.py                  # menu principal (Tkinter) que liga todos os módulos
├── abrir_ots.py             # abre só a janela das ordens de trabalho
├── db/
│   ├── connection.py        # get_connection() e inicializar_bd()
│   └── schema.sql           # tabelas
├── docs/                    # relatórios Excel gerados
├── src/
│   ├── models/              # classes de dados (Cliente, Viatura, OrdemTrabalho, ...)
│   ├── repositories/        # SQL
│   ├── services/            # regras de negócio
│   ├── controllers/         # ligação entre views e services
│   └── views/               # janelas Tkinter (estilo.py tem o aspeto comum)
├── tests/                   # testes por módulo
└── tests_tecnicos_pecas/    # testes de técnicos e peças
```

## Regras principais das ordens de trabalho

- Cada OT tem de ter **viatura** e **técnico** (ambos têm de existir).
- Estados: `Pendente`, `Em Curso`, `Aguarda Peça`, `Concluída` e `Entregue`. Só se pode **entregar** uma OT que esteja **Concluída**, e uma OT entregue deixa de poder ser alterada.
- O **custo total** da OT é recalculado sempre que se adiciona ou remove uma linha.
- Linhas de tipo `mao_obra` não podem ter peça (as horas trabalhadas entram no valor da fatura); linhas de tipo `peca` têm de indicar a peça usada.
- Cada OT só pode ter **uma fatura**, e só se gera a fatura de uma OT com linhas.

## Trabalho em grupo (Git)

- Cada pessoa trabalha no seu branch (`feature/...`) e integra a `main` por Pull Request.
- Antes de começar a trabalhar, trazer a `main` para o branch: `git fetch origin` e `git merge origin/main`.
- O `.gitignore` ignora `__pycache__/` e `*.db`. Não fazer commit de ficheiros `.pyc` nem da base de dados.
