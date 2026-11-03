class Tecnico:

    def __init__(self, nome, especialidade, custo_hora, ativo=True, id_tecnico=None):
        self.id_tecnico = id_tecnico
        self.nome = nome
        self.especialidade = especialidade
        self.custo_hora = custo_hora
        self.ativo = ativo

    def __str__(self):
        return "Técnico " + str(self.id_tecnico) + ": " + self.nome
