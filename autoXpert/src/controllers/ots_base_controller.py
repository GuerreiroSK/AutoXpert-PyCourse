class OtsBaseController:
    # Funções comuns a todos os controllers: converter o texto que vem da janela
    # e transformar erros em mensagens para o utilizador.
    # Cada controller herda desta classe:  class OrdemTrabalhoController(OtsBaseController)

    # Mensagem quando a base de dados recusa um id que não existe (chave estrangeira).
    # Cada controller pode mudá-la para falar das suas entidades.
    MENSAGEM_FK = "Um dos registos indicados não existe"

    # "" ou só espaços -> None; senão devolve o texto sem espaços nas pontas
    def _texto_ou_none(self, texto):
        if texto is None:
            return None
        texto = str(texto).strip()
        if texto == "":
            return None
        return texto

    # Converte para inteiro. Se estiver vazio devolve None (quando é obrigatório,
    # o service é que recusa). Se não for um número inteiro, dá erro com mensagem clara.
    def _para_inteiro(self, texto, nome_campo):
        texto = self._texto_ou_none(texto)
        if texto is None:
            return None
        try:
            return int(texto)
        except ValueError:
            raise ValueError(nome_campo + " tem de ser um número inteiro")

    # Converte para decimal; aceita vírgula ou ponto (40,5 ou 40.5)
    def _para_decimal(self, texto, nome_campo):
        texto = self._texto_ou_none(texto)
        if texto is None:
            return None
        try:
            return float(texto.replace(",", "."))
        except ValueError:
            raise ValueError(nome_campo + " tem de ser um número")

    # Transforma uma exceção numa mensagem para o utilizador
    def _texto_do_erro(self, erro):
        if isinstance(erro, ValueError):
            return str(erro)
        if "FOREIGN KEY" in str(erro).upper():
            return self.MENSAGEM_FK
        return "Erro na base de dados: " + str(erro)
