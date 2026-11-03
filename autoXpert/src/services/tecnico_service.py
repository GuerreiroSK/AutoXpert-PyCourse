from dataclasses import replace

from src.models.tecnico import Tecnico
from src.repositories import tecnico_repository as repository
from src.services.validacao import texto_obrigatorio, validar_valor


class TecnicoService:
    """Aplica as regras antes de pedir ao repositorio que guarde os dados."""

    def listar(self, apenas_ativos: bool = False) -> list[Tecnico]:
        linhas = repository.listar_tecnicos(apenas_ativos)
        tecnicos: list[Tecnico] = []

        for linha in linhas:
            tecnico = Tecnico.da_linha(linha)
            tecnicos.append(tecnico)

        return tecnicos

    def obter(self, id_tecnico: int) -> Tecnico:
        linha = repository.obter_tecnico(id_tecnico)
        if linha is None:
            raise ValueError("O tecnico selecionado ja nao existe.")
        return Tecnico.da_linha(linha)

    def guardar(self, tecnico: Tecnico) -> Tecnico:
        nome = texto_obrigatorio(tecnico.nome, "Nome")
        especialidade = (tecnico.especialidade or "").strip() or None
        validar_valor(tecnico.custo_hora, "Custo/hora")
        if not isinstance(tecnico.ativo, bool):
            raise ValueError("O estado ativo deve ser verdadeiro ou falso.")

        if tecnico.id_tecnico is None:
            id_tecnico = repository.criar_tecnico(
                nome, especialidade, tecnico.custo_hora, tecnico.ativo
            )
        else:
            id_tecnico = tecnico.id_tecnico
            atualizado = repository.atualizar_tecnico(
                id_tecnico, nome, especialidade, tecnico.custo_hora, tecnico.ativo
            )
            if not atualizado:
                raise ValueError("O tecnico selecionado ja nao existe.")
        return replace(tecnico, id_tecnico=id_tecnico, nome=nome, especialidade=especialidade)

    def eliminar(self, id_tecnico: int) -> None:
        if not repository.eliminar_tecnico(id_tecnico):
            raise ValueError("O tecnico selecionado ja nao existe.")
