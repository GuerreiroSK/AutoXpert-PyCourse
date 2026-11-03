from src.services.validacao import texto_obrigatorio, validar_valor


class TecnicoService:
    # Regras dos técnicos. O SQL fica no repositório (recebido no construtor).

    def __init__(self, tecnico_repository):
        self.repository = tecnico_repository

    def listar(self, apenas_ativos=False):
        return self.repository.listar_todos(apenas_ativos)

    def obter(self, id_tecnico):
        tecnico = self.repository.obter_por_id(id_tecnico)
        if tecnico is None:
            raise ValueError("O técnico selecionado já não existe.")
        return tecnico

    # Cria o técnico (sem id) ou atualiza-o (com id). Devolve o técnico guardado.
    def guardar(self, tecnico):
        tecnico.nome = texto_obrigatorio(tecnico.nome, "Nome")
        tecnico.especialidade = (tecnico.especialidade or "").strip() or None
        validar_valor(tecnico.custo_hora, "Custo/hora")
        if not isinstance(tecnico.ativo, bool):
            raise ValueError("O estado ativo deve ser verdadeiro ou falso.")

        if tecnico.id_tecnico is None:
            return self.repository.inserir(tecnico)

        if not self.repository.atualizar(tecnico):
            raise ValueError("O técnico selecionado já não existe.")
        return tecnico

    def eliminar(self, id_tecnico):
        if not self.repository.eliminar(id_tecnico):
            raise ValueError("O técnico selecionado já não existe.")
