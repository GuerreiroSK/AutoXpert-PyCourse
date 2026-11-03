# AutoXpert – lista de alterações (limpeza e uniformização)

Resumo do que foi encontrado no código que estava na `main`, o que foi mudado e o que fica por decidir.
Resultado final: **436 testes a passar**, `main.py` a arrancar com os 7 módulos.

## 1. Problemas encontrados e como ficaram

| # | Onde estava o problema | O que foi feito |
|---|---|---|
| 1 | `README.md` com 2 linhas | README novo: como correr, requisitos, primeiro uso, estrutura, regras, testes, Git |
| 2 | `.gitignore` incompleto; `db/autoxpert.db` e ficheiros `.pyc` chegaram a ir para o Git | `.gitignore` completo (`__pycache__/`, `*.pyc`, `*.db`, `docs/*.xlsx`, `.venv/`, `.vscode/`, ...) |
| 3 | `main.py` e 2 repositórios (`log_alteracao_ot_repository.py`, `viatura_repository.py`) com marcas de conflito do Git na `origin/main` | Resolvidos (já em `main`); `main.py` novo liga todos os módulos |
| 4 | Repositórios de Técnicos/Peças vazios (0 bytes) no commit `71b6ba2` | Escritos / substituídos pelos da colega, já corrigidos |
| 5 | Sem ficheiros de apoio | Criados `requirements.txt`, `docs/.gitkeep` e este documento |
| 6 | Dois sítios para testes (`tests/` e `tests_tecnicos_pecas/`) | Tudo em `tests/<entidade>_testes/`; pasta antiga apagada; testes de técnicos e peças reescritos |
| 7 | Nomes de ficheiros diferentes de módulo para módulo | Regra única `<entidade>_<camada>.py` (ex.: `peca_service.py`); testes `test_<entidade>_<camada>.py` |
| 8 | Dois estilos de repositório (classe com ligação injetada vs funções soltas/`get_connection()` dentro) | Um só: classe com `conexao` no construtor, que devolve objetos do model |
| 9 | Serviços de **Log** e **Viatura** a escreverem SQL diretamente na `conexao` | Passam a usar `LogAlteracaoOTRepository` e `ViaturaRepository` (e o repositório de clientes/OTs) |
| 10 | Erros mostrados de várias maneiras nas views (`messagebox` em vários sítios, `mensagens.py`, `print`, etc.) | Uma só: `estilo.py` (`mostrar_erro`, `mostrar_info`, `perguntar_sim_nao`, `executar_acao`). `mensagens.py` apagado |
| 11 | Código acima do nível do curso: `lambda`, `dataclass`, anotações de tipos, `*args/**kwargs`, `:.2f`, `:02d`, `sum()/max()`, `if __name__ == "__main__"`, f-strings | Reescrito com o que demos (`round()`, ciclos `for`, concatenação, `if/else`) |
| 12 | `abrir_ots.py` | Apagado (a OT abre pelo menu principal) |
| 13 | Teste "fake" de Viatura (`test_viatura_service_com_fake.py`) obsoleto | Apagado (os testes passam a usar `MagicMock`/BD em memória) |

## 2. Erros de comportamento encontrados (e corrigidos)

- **Histórico da viatura:** o controller passava o `id_viatura` mas o service esperava a **matrícula** → corrigido, com testes.
- **Menu do Registo de alterações:** não funcionava no menu principal → corrigido ao ligar tudo em `main.py`.
- **Técnicos e Peças** não apareciam no menu principal da aplicação (só tínhamos Tkinter à parte) → ligados.
- O `main.py` da `main` não era o que testámos (tinha o código antigo em conflito) → substituído.

## 3. Novos testes

- `tests/tecnico_testes/` e `tests/peca_testes/`: modelo, repositório (BD em memória), service (`MagicMock`), controller e view.
- Testes de repositório (BD em memória) para **Cliente, Fatura, Viatura e Log**.
- `tests/bd_testes/base_dados_teste.py`: `criar_conexao_vazia()` e `criar_conexao_teste()`.

## 4. Pontos em aberto (para o grupo decidir)

1. **Nomes dos métodos dos repositórios** ainda diferem: `criar` (Viatura, OT), `inserir` (Cliente, Fatura, Técnico, Peça), `registar` (Log), `obter_por_id` / `procurar_por_id`. Proposta: unificar em `inserir`, `obter_por_id`, `listar_todos`, `atualizar`, `eliminar`.
2. **`db/autoxpert.db` continua no Git** (tem 1 cliente e 1 viatura de teste). Se todos concordarem: `git rm --cached db/autoxpert.db`.
3. **`km_estrada`** no código vs **"km_entrada"** no enunciado: confirmar qual é o nome certo.
4. **`LogAlteracaoOT` não tem `utilizador_id`** (o enunciado pode pedir).
5. A janela de OTs **ainda não grava no Log** quando se altera uma OT (só o consulta).
