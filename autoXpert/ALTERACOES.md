# AutoXpert – lista de alterações (limpeza e uniformização)

O que foi encontrado no código que estava na `main`, o que foi mudado e porquê.
Resultado: **444 testes a passar**, `main.py` a arrancar com os 7 módulos.

## 1. Problemas encontrados e como ficaram

| # | Onde estava o problema | O que foi feito |
|---|---|---|
| 1 | `README.md` com 2 linhas | README novo: como correr, requisitos, primeiro uso, estrutura, regras, testes, Git |
| 2 | `.gitignore` incompleto; `db/autoxpert.db` e ficheiros `.pyc` chegaram a ir para o Git | `.gitignore` completo; `autoxpert.db` deixa de ser seguido pelo Git (ver ponto 14) |
| 3 | `main.py` e 2 repositórios (`log_alteracao_ot_repository.py`, `viatura_repository.py`) com marcas de conflito do Git na `origin/main` | Resolvidos; `main.py` novo liga todos os módulos |
| 4 | Repositórios de Técnicos/Peças vazios (0 bytes) no commit `71b6ba2` | Escritos / substituídos pelos da colega, já corrigidos |
| 5 | Sem ficheiros de apoio | Criados `requirements.txt`, `docs/.gitkeep` e este documento |
| 6 | Dois sítios para testes (`tests/` e `tests_tecnicos_pecas/`) | Tudo em `tests/<entidade>_testes/`; pasta antiga apagada; testes de técnicos e peças reescritos |
| 7 | Nomes de ficheiros diferentes de módulo para módulo | Regra única `<entidade>_<camada>.py` (ex.: `peca_service.py`); testes `test_<entidade>_<camada>.py` |
| 8 | Dois estilos de repositório (classe com ligação injetada vs funções soltas) | Um só: classe com `conexao` no construtor, que devolve objetos do model |
| 9 | Serviços de **Log** e **Viatura** a escreverem SQL diretamente na `conexao` | Passam a usar `LogAlteracaoOTRepository` e `ViaturaRepository` |
| 10 | Erros mostrados de várias maneiras nas views (`messagebox` em vários sítios, `mensagens.py`) | Uma só: `estilo.py` (`mostrar_erro`, `mostrar_info`, `perguntar_sim_nao`, `executar_acao`). `mensagens.py` apagado |
| 11 | Código acima do nível do curso: `lambda`, `dataclass`, anotações de tipos, `*args/**kwargs`, `:.2f`, `:02d`, `sum()/max()`, `if __name__ == "__main__"`, f-strings | Reescrito com o que demos (`round()`, ciclos `for`, concatenação, `if/else`) |
| 12 | `abrir_ots.py` | Apagado (a OT abre pelo menu principal) |
| 13 | Teste "fake" de Viatura (`test_viatura_service_com_fake.py`) obsoleto | Apagado (os testes usam `MagicMock` ou BD em memória) |
| 14 | `db/autoxpert.db` (com dados de teste) guardado no Git | Retirado do Git com `git rm --cached`; cada pessoa tem a sua BD, criada a partir de `db/schema.sql` |
| 15 | Métodos dos repositórios com nomes diferentes (`criar`, `registar`, `procurar_por_id`, `apagar`, `listar`, `listar_todas`) | Nomes iguais em todos: `inserir`, `obter_por_id`, `listar_todos`, `atualizar`, `eliminar` (e `eliminar_por_ot`). `inserir` devolve sempre o objeto com o `id` preenchido |
| 16 | Campo `km_estrada` (nome errado, não corresponde ao enunciado) | Renomeado para `km_entrada` no schema, model, repositório, service, controller, view e testes. No ecrã aparece como **"KM da viatura"** |
| 17 | O Log só se podia consultar: nada o preenchia | O `OrdemTrabalhoService` regista no Log cada mudança de **estado** e de **técnico** (valor anterior e novo). Criar uma OT, ou "mudar" para o mesmo valor, não regista nada |

## 2. Erros de comportamento encontrados (e corrigidos)

- **Histórico da viatura:** o controller passava o `id_viatura` mas o service esperava a **matrícula**. Corrigido, com testes.
- **Menu do Registo de alterações:** não funcionava no menu principal. Corrigido ao ligar tudo em `main.py`.
- **Técnicos e Peças** não apareciam no menu principal. Já aparecem.
- O `main.py` da `main` não era o que testámos (tinha o código antigo em conflito). Substituído.

## 3. Testes

- `tests/tecnico_testes/` e `tests/peca_testes/`: modelo, repositório (BD em memória), service (`MagicMock`), controller e view.
- Testes de repositório (BD em memória) para **Cliente, Fatura, Viatura e Log**.
- Testes do registo no Log (unitários e de integração) para o estado e o técnico das OTs.
- `tests/bd_testes/base_dados_teste.py`: `criar_conexao_vazia()` e `criar_conexao_teste()`.

## 4. Depois do merge (cada pessoa)

1. `git pull` na `main` (muitos ficheiros mudaram de nome).
2. Se existir um `db/autoxpert.db` antigo, **apagá-lo**: o schema mudou (`km_entrada`) e a aplicação cria uma BD nova no arranque.
3. Atualizar os branches de trabalho com `git merge origin/main`.

## 5. Notas finais

- **Constructor do `OrdemTrabalhoService`:** passou a receber também o `LogAlteracaoOTService`: `OrdemTrabalhoService(repo_ot, log_service)`.
- **Log:** só regista alterações de estado e de técnico, porque são as únicas que a aplicação permite fazer a uma OT depois de criada. Se um dia se puder editar mais campos, é acrescentar a chamada ao Log no service.
- **Por decidir:** o `LogAlteracaoOT` não tem `utilizador_id` (não há utilizadores/login na aplicação). Só vale a pena se o enunciado o pedir.
