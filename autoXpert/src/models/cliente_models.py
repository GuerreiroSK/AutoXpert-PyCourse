class Cliente:
    def __init__(
        self,
        nome,
        nif=None,
        telefone=None,
        email=None,
        morada=None,
        data_registo=None,
        id_cliente=None
    ):
        self.id_cliente = id_cliente
        self.nome = nome
        self.nif = nif
        self.telefone = telefone
        self.email = email
        self.morada = morada
        self.data_registo = data_registo

    def __str__(self):
        return f"Cliente {self.id_cliente}: {self.nome}"
