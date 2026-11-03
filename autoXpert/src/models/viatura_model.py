class Viatura:

    def __init__(self, matricula, marca, modelo, id_cliente, id_viatura=None,
                 ano=None, cor=None, km_entrada=0):
        self.id_viatura = id_viatura
        self.matricula = matricula
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.cor = cor
        self.km_entrada = km_entrada
        self.id_cliente = id_cliente

    def atualizar_dados(self, marca, modelo, ano, cor, km_entrada):
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.cor = cor
        self.km_entrada = km_entrada

    def __str__(self):
        return "Viatura " + str(self.id_viatura) + ": " + self.matricula
