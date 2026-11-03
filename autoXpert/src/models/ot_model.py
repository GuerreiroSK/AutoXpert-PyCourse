class OrdemTrabalho:
    
    # Estados possíveis de uma OT (RF06), pela ordem do fluxo.
    ESTADO_PENDENTE = "Pendente"
    ESTADO_EM_CURSO = "Em Curso"
    ESTADO_AGUARDA_PECA = "Aguarda Peça"
    ESTADO_CONCLUIDA = "Concluída"
    ESTADO_ENTREGUE = "Entregue"

    ESTADOS = [ESTADO_PENDENTE, ESTADO_EM_CURSO, ESTADO_AGUARDA_PECA,
               ESTADO_CONCLUIDA, ESTADO_ENTREGUE]

    def __init__(self, id_viatura, id_tecnico, data_entrada, data_prev_saida,
                 descricao_avaria, estado=ESTADO_PENDENTE, data_saida_real=None,
                 custo_total=0, id_ot=None):
        
        # A rececionista tem de indicar o técnico logo ao criar a OT
        if id_tecnico is None:
            raise ValueError("A OT tem de ter um técnico responsável")
        if estado not in OrdemTrabalho.ESTADOS:
            raise ValueError("Estado inválido: " + str(estado))

        self.id_ot = id_ot
        self.id_viatura = id_viatura
        self.id_tecnico = id_tecnico
        self.data_entrada = data_entrada
        self.data_prev_saida = data_prev_saida
        self.data_saida_real = data_saida_real
        self.estado = estado
        self.descricao_avaria = descricao_avaria
        self.custo_total = custo_total

    def __str__(self):
        return ("OT " + str(self.id_ot) + " | viatura " + str(self.id_viatura)
                + " | técnico " + str(self.id_tecnico)
                + " | estado: " + str(self.estado)
                + " | custo: " + str(self.custo_total))