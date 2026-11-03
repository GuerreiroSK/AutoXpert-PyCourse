class LogAlteracaoOT:

    def __init__(self, id_ot, data_hora, campo_alterado, id_log=None,
                 valor_anterior=None, valor_novo=None):
        self.id_log = id_log
        self.id_ot = id_ot
        self.data_hora = data_hora
        self.campo_alterado = campo_alterado
        self.valor_anterior = valor_anterior
        self.valor_novo = valor_novo

    def obter_resumo(self):
        return (
            "OT " + str(self.id_ot)
            + " | Campo: " + str(self.campo_alterado)
            + " | Anterior: " + str(self.valor_anterior)
            + " | Novo: " + str(self.valor_novo)
            + " | Data: " + str(self.data_hora)
        )
