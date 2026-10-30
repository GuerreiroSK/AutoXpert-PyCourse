from src.models.ordem_trabalho_model import OrdemTrabalho

class OrdemTrabalhoRepository:

    # Colunas com o alias "o" para não haver ambiguidade quando se junta a tabela Viatura
    COLUNAS = ("o.id_ot, o.id_viatura, o.id_tecnico, o.data_entrada, "
               "o.data_prev_saida, o.data_saida_real, o.estado, "
               "o.descricao_avaria, o.custo_total")
    BASE_SELECT = "SELECT " + COLUNAS + " FROM OrdemTrabalho o"
    
    # Listagens: as OTs mais recentes primeiro
    ORDENACAO = " ORDER BY o.data_entrada DESC, o.id_ot DESC"

    def __init__(self, conexao):
        self.conexao = conexao

    # Converte uma linha da base de dados (tuplo) num objeto OrdemTrabalho
    def _linha_para_objeto(self, linha):
        return OrdemTrabalho(
            id_ot=linha[0],
            id_viatura=linha[1],
            id_tecnico=linha[2],
            data_entrada=linha[3],
            data_prev_saida=linha[4],
            data_saida_real=linha[5],
            estado=linha[6],
            descricao_avaria=linha[7],
            custo_total=linha[8],
        )

    # Executa um SELECT e devolve uma lista de objetos OrdemTrabalho
    def _listar_com_sql(self, sql, parametros):
        cursor = self.conexao.cursor()
        cursor.execute(sql, tuple(parametros))
        resultado = []
        for linha in cursor.fetchall():
            resultado.append(self._linha_para_objeto(linha))
        return resultado

    # ---------- CRUD básico ----------

    # RF03: grava uma nova OT e preenche o id gerado pela base de dados
    def inserir(self, ot):
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO OrdemTrabalho (id_viatura, id_tecnico, data_entrada, "
            "data_prev_saida, data_saida_real, estado, descricao_avaria, custo_total) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (ot.id_viatura, ot.id_tecnico, ot.data_entrada, ot.data_prev_saida,
             ot.data_saida_real, ot.estado, ot.descricao_avaria, ot.custo_total),
        )
        self.conexao.commit()
        ot.id_ot = cursor.lastrowid
        return ot

    def listar(self):
        return self._listar_com_sql(self.BASE_SELECT + self.ORDENACAO, [])

    # Devolve a OT ou None se o id não existir
    def procurar_por_id(self, id_ot):
        lista = self._listar_com_sql(self.BASE_SELECT + " WHERE o.id_ot = ?", [id_ot])
        if len(lista) == 0:
            return None
        return lista[0]

    # Atualiza todos os campos da OT; devolve True se a OT existia
    def atualizar(self, ot):
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE OrdemTrabalho SET id_viatura = ?, id_tecnico = ?, "
            "data_entrada = ?, data_prev_saida = ?, data_saida_real = ?, "
            "estado = ?, descricao_avaria = ?, custo_total = ? WHERE id_ot = ?",
            (ot.id_viatura, ot.id_tecnico, ot.data_entrada, ot.data_prev_saida,
             ot.data_saida_real, ot.estado, ot.descricao_avaria, ot.custo_total,
             ot.id_ot),
        )
        self.conexao.commit()
        return cursor.rowcount > 0

    # Só funciona se a OT já não tiver linhas (apagar primeiro as linhas)
    def apagar(self, id_ot):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM OrdemTrabalho WHERE id_ot = ?", (id_ot,))
        self.conexao.commit()
        return cursor.rowcount > 0

    # ---------- Alterações pontuais (RF05, RF06, RF13) ----------

    # RF06: muda só o estado. As regras de transição ficam no service.
    def mudar_estado(self, id_ot, novo_estado):
        if novo_estado not in OrdemTrabalho.ESTADOS:
            raise ValueError("Estado inválido: " + str(novo_estado))
        cursor = self.conexao.cursor()
        cursor.execute("UPDATE OrdemTrabalho SET estado = ? WHERE id_ot = ?",
                       (novo_estado, id_ot))
        self.conexao.commit()
        return cursor.rowcount > 0

    # RF05: atribui (ou troca) o técnico responsável
    def atribuir_tecnico(self, id_ot, id_tecnico):
        cursor = self.conexao.cursor()
        cursor.execute("UPDATE OrdemTrabalho SET id_tecnico = ? WHERE id_ot = ?",
                       (id_tecnico, id_ot))
        self.conexao.commit()
        return cursor.rowcount > 0

    # RF13: guarda o custo total calculado pelo service a partir das linhas
    def atualizar_custo_total(self, id_ot, custo_total):
        cursor = self.conexao.cursor()
        cursor.execute("UPDATE OrdemTrabalho SET custo_total = ? WHERE id_ot = ?",
                       (custo_total, id_ot))
        self.conexao.commit()
        return cursor.rowcount > 0

    # ---------- Pesquisas (RF07, RF12, RF14) ----------

    # RF07: histórico de uma viatura, pelo id
    def listar_por_viatura(self, id_viatura):
        return self._listar_com_sql(
            self.BASE_SELECT + " WHERE o.id_viatura = ?" + self.ORDENACAO,
            [id_viatura])

    # RF07: histórico pela matrícula (ignora maiúsculas/minúsculas).
    # Assume que a tabela Viatura tem as colunas id_viatura e matricula.
    def listar_por_matricula(self, matricula):
        sql = (self.BASE_SELECT
               + " JOIN Viatura v ON o.id_viatura = v.id_viatura"
               + " WHERE UPPER(v.matricula) = UPPER(?)" + self.ORDENACAO)
        return self._listar_com_sql(sql, [matricula])

    # RF14: OTs "Em Curso" ou "Aguarda Peça"
    def listar_em_curso(self):
        return self._listar_com_sql(
            self.BASE_SELECT + " WHERE o.estado IN (?, ?)" + self.ORDENACAO,
            [OrdemTrabalho.ESTADO_EM_CURSO, OrdemTrabalho.ESTADO_AGUARDA_PECA])

    # RF12: filtra por data de entrada (AAAA-MM-DD), estado e técnico.
    # Os filtros que não forem indicados (None) são ignorados.
    # Também serve para o técnico ver só as suas OTs (RNF02): pesquisar(id_tecnico=3)
    def pesquisar(self, data_inicio=None, data_fim=None, estado=None, id_tecnico=None):
        sql = self.BASE_SELECT + " WHERE 1 = 1"
        parametros = []
        if data_inicio is not None:
            sql += " AND date(o.data_entrada) >= ?"
            parametros.append(data_inicio)
        if data_fim is not None:
            sql += " AND date(o.data_entrada) <= ?"
            parametros.append(data_fim)
        if estado is not None:
            sql += " AND o.estado = ?"
            parametros.append(estado)
        if id_tecnico is not None:
            sql += " AND o.id_tecnico = ?"
            parametros.append(id_tecnico)
        sql += self.ORDENACAO
        return self._listar_com_sql(sql, parametros)