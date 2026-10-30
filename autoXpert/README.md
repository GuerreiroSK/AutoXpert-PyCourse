# AutoXpert-PyCourse
Projeto de grupo IEFP em Python.

## Executar

Requer Python 3.10 ou superior, com Tkinter e SQLite (incluidos na instalacao
oficial do Python para Windows). Nao e necessario instalar pacotes com pip.
No PowerShell:

```powershell
Set-Location C:\workspace\iefpe\fundamentosPython\aula07\exercicio7\autoXpert
python main.py
```

Abre uma janela com dois separadores: **Tecnicos** e **Pecas**.
A base de dados e `db\autoxpert.db`. O arranque cria apenas as tabelas em falta,
nao apaga os dados existentes. Para inicializar sem abrir a janela:

```powershell
python main.py --inicializar-bd
```

O projeto foi recuperado do ZIP fornecido, pois a pasta da implementacao anterior
ja nao estava presente nesta sessao. Os exercicios de vendas e aluguer nao foram
alterados. O ZIP tinha as camadas vazias; optou-se por Tkinter, tambem usado nos
exercicios, sem introduzir um servidor web ou dependencias externas.

## 1. Compreender as camadas

| Camada | Tecnico | Peca | Responsabilidade |
|---|---|---|---|
| Model | `src\models\tecnico.py` | `src\models\peca.py` | Representa os dados em objetos Python. |
| Repository | `src\repositories\tecnico_repository.py` | `src\repositories\pecas_repository.py` | Executa o SQL e devolve linhas SQLite. |
| Service | `src\services\tecnico_service.py` | `src\services\peca_service.py` | Valida dados e aplica regras. |
| Controller | `src\controllers\tecnico_controller.py` | `src\controllers\peca_controller.py` | Converte texto do formulario e chama o servico. |
| View | `src\views\tecnico_view.py` | `src\views\peca_view.py` | Desenha os campos, botoes e tabelas. |
| Main | `main.py` | `main.py` | Inicializa a BD e liga as paginas, controllers e servicos. |

Esta tabela apresenta a organizacao dos ficheiros. Quando se clica num botao,
o fluxo e **View -> Controller -> Service -> Repository -> SQLite**.
No regresso, o Service transforma as linhas em Models para a View apresentar.
Os repositories existentes sao reutilizados: nao ha uma segunda copia chamada
`peca_repository.py`. Os repositories de Viatura e Log da etapa anterior tambem
foram recuperados, mas nao recebem paginas novas nesta etapa.

### Exemplo: guardar um tecnico

1. A View le o texto dos campos, como `"Ana"` e `"20,50"`.
2. O Controller converte o custo para o numero `20.5` e cria um objeto `Tecnico`.
   O ficheiro `conversoes.py` permite usar virgula ou ponto decimal, sem
   separadores de milhares. Valores como `"vinte"` geram uma mensagem clara.
3. O Service retira espacos exteriores, exige nome, custo finito e nao negativo,
   e estado ativo booleano. Continua a validar mesmo que outra interface o use.
4. O Repository executa `INSERT` se for novo ou `UPDATE` se tiver ID.
   Os valores sao enviados nos parametros `?`, separados do SQL.
5. `with conn` faz commit se a escrita correr bem e rollback se ocorrer um erro;
   `closing` fecha a ligacao em qualquer dos casos.
6. O Model usa `@dataclass` para criar automaticamente o construtor.
   `id_tecnico=None` representa um tecnico ainda por guardar. A conversao
   `da_linha` transforma um registo SQLite num objeto com atributos.
7. A View atualiza a tabela e mostra uma mensagem de confirmacao no rodape.
   Erros esperados sao apresentados em caixas de aviso, sem limpar o formulario.

### Aprender por etapas: listar registos

Comece pelo metodo `listar` em `src\services\tecnico_service.py`.
O codigo usa um ciclo `for` para mostrar cada passo:

```python
linhas = repository.listar_tecnicos(apenas_ativos)
tecnicos: list[Tecnico] = []

for linha in linhas:
    tecnico = Tecnico.da_linha(linha)
    tecnicos.append(tecnico)

return tecnicos
```

1. `linhas` recebe os registos da base de dados.
2. `tecnicos` comeca como uma lista vazia. `list[Tecnico]` indica que essa lista
   vai conter objetos `Tecnico`; e uma anotacao de tipo.
3. O `for` percorre um registo de cada vez.
4. `da_linha` transforma esse registo num objeto com campos como `nome`.
5. `append` acrescenta o objeto a lista; `return` devolve a lista completa.

O metodo `listar` de `PecaService` segue os mesmos passos. Antes do ciclo,
um `if/else` escolhe entre todas as pecas e apenas as que tem stock baixo.
Em `src\models\peca.py`, `da_linha` indica cada campo pelo nome, em vez de usar
`**dict(linha)`, para ser mais facil acompanhar a conversao.

Estas primeiras simplificacoes mantem as camadas, os filtros e as validacoes.
O objetivo e tornar os passos visiveis, nao escrever o menor numero de linhas.

## 2. Usar Tecnicos

1. Clique em **Novo**, preencha nome, especialidade opcional e custo/hora.
2. Marque **Ativo** e clique em **Guardar**.
3. Selecione uma linha para carregar os dados, altere-os e volte a guardar.
4. **Apenas ativos** filtra a lista. **Atualizar lista** volta a consultar a BD
   e limpa o formulario; nao guarda alteracoes por si.
5. **Eliminar** pede confirmacao. Se houver uma OT ligada, a chave estrangeira
   impede a eliminacao. Nesse caso, pode desativar o tecnico sem apagar o historico.

## 3. Usar Pecas

1. Clique em **Nova** e preencha referencia unica, nome, precos, stock inicial,
   stock minimo e fornecedor opcional. Clique em **Guardar**.
2. Ao selecionar uma peca, o stock atual fica apenas de leitura. Guardar altera
   o catalogo, nao substitui stock; assim nao se perde um movimento de stock.
3. Para uma rececao, selecione a peca, indique quantidade positiva, fornecedor
   e preco de compra nos campos do formulario e clique em **Receber stock**.
   Esta acao aumenta o stock e atualiza apenas fornecedor e custo de compra;
   outras edicoes do formulario precisam de **Guardar**.
4. Para uma saida, indique, por exemplo, `-2` e clique em **Ajustar (+/-)**.
   O valor representa uma variacao, nao um novo saldo. Nao pode deixar
   stock negativo; zero e fracoes tambem nao sao movimentos validos.
5. Stock atual menor ou igual ao minimo aparece destacado e com o texto
   **Stock baixo**. O filtro **Apenas stock baixo** mostra essas pecas.
6. Referencias repetidas e eliminacao de uma peca usada numa OT geram erro
   explicito. A base de dados protege essas regras com UNIQUE, CHECK e FK.

Os precos mantem o tipo REAL do esquema fornecido; nao foram alteradas as tabelas.
Nao ha ainda registo separado do historico dos movimentos de stock.
Estas paginas nao implementam a atribuicao de OTs ou os relatorios de faturacao,
que pertencem a outras funcionalidades do projeto.

## 4. Executar os testes

Dentro de `autoXpert`, execute:

```powershell
python -B -m unittest discover -s tests_tecnicos_pecas -v
```

Os testes de models e services sao unitarios; os testes de repositories usam
SQLite temporario e os testes de views criam janelas Tkinter com controllers
simulados. `base_dados_temporaria.py` cria uma BD temporaria e nao escreve em
`db\autoxpert.db`. O parametro `-B` evita criar ficheiros de bytecode.

- `test_models_tecnicos_pecas.py`: testa os modelos e conversoes de linhas SQLite.
- `test_controllers_tecnicos_pecas.py`: testa conversoes dos formularios e chamadas aos services.
- `test_services_tecnicos_pecas.py`: testa regras e validacoes com repositories simulados.
- `test_repositories_tecnicos_pecas.py`: testa operacoes SQL numa BD temporaria.
- `test_views_tecnicos_pecas.py`: testa o envio dos dados das paginas aos controllers.
  Requer ambiente grafico disponivel.

`assertEqual` verifica o resultado esperado; `assertRaises` verifica que um dado
invalido gera erro. Para estudar, comece em `test_controllers_tecnicos_pecas.py`
e siga a chamada de guardar para o service.
