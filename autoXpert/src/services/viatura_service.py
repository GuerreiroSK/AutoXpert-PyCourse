
class ViaturaService:

    def __init__(self, viatura_repository, conexao):
        self.viatura_repository = viatura_repository
        self.conexao = conexao

    def registar_viatura(self, viatura):
        # Validar campos obrigatórios
        if not viatura.matricula.strip():
            raise ValueError("A matrícula é obrigatória.")

        if not viatura.marca.strip():
            raise ValueError("A marca é obrigatória.")

        if not viatura.modelo.strip():
            raise ValueError("O modelo é obrigatório.")

        if viatura.id_cliente <= 0:
            raise ValueError("O cliente indicado é inválido.")

        if viatura.km_estrada < 0:
            raise ValueError("Os quilómetros não podem ser negativos.")

        # Verificar se o cliente existe
        cursor = self.conexao.cursor()
        cursor.execute(
            "SELECT id_cliente FROM Cliente WHERE id_cliente = ?",
            (viatura.id_cliente,)
        )

        if cursor.fetchone() is None:
            raise ValueError("O cliente indicado não existe.")

        # Verificar se a matrícula já está registada
        existente = self.viatura_repository.obter_por_matricula(
            viatura.matricula
        )

        if existente is not None:
            raise ValueError("Já existe uma viatura com esta matrícula.")

        return self.viatura_repository.criar(viatura)

    def consultar_por_id(self, id_viatura):
        if id_viatura <= 0:
            raise ValueError("ID da viatura inválido.")

        viatura = self.viatura_repository.obter_por_id(id_viatura)

        if viatura is None:
            raise ValueError("Viatura não encontrada.")

        return viatura

    def consultar_por_matricula(self, matricula):
        if not matricula or not matricula.strip():
            raise ValueError("Indique uma matrícula.")

        viatura = self.viatura_repository.obter_por_matricula(
            matricula.strip()
        )

        if viatura is None:
            raise ValueError("Viatura não encontrada.")

        return viatura

    def listar_viaturas(self):
        return self.viatura_repository.listar_todas()

    def atualizar_viatura(self, viatura):
        if viatura.id_viatura is None:
            raise ValueError("A viatura não tem um ID válido.")

        if not viatura.matricula.strip():
            raise ValueError("A matrícula é obrigatória.")

        if not viatura.marca.strip():
            raise ValueError("A marca é obrigatória.")

        if not viatura.modelo.strip():
            raise ValueError("O modelo é obrigatório.")

        if viatura.km_estrada < 0:
            raise ValueError("Os quilómetros não podem ser negativos.")

        atual = self.viatura_repository.obter_por_id(
            viatura.id_viatura
        )

        if atual is None:
            raise ValueError("Viatura não encontrada.")

        outra = self.viatura_repository.obter_por_matricula(
            viatura.matricula
        )

        if outra is not None and outra.id_viatura != viatura.id_viatura:
            raise ValueError("Esta matrícula já pertence a outra viatura.")

        return self.viatura_repository.atualizar(viatura)

    def eliminar_viatura(self, id_viatura):
        viatura = self.viatura_repository.obter_por_id(id_viatura)

        if viatura is None:
            raise ValueError("Viatura não encontrada.")

        return self.viatura_repository.eliminar(id_viatura)

    def consultar_historico(self, matricula):
        viatura = self.consultar_por_matricula(matricula)

        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT
                ot.id_ot,
                ot.data_entrada,
                ot.data_prev_saida,
                ot.data_saida_real,
                ot.estado,
                ot.descricao_avaria,
                ot.custo_total
            FROM OrdemTrabalho ot
            WHERE ot.id_viatura = ?
            ORDER BY ot.data_entrada DESC
        """, (viatura.id_viatura,))

        return cursor.fetchall()
