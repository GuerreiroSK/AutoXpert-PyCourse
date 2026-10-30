from datetime import datetime, date

from src.models.ordem_trabalho_model import OrdemTrabalho
from src.models.linha_ot_model import LinhaOT

class OrdemTrabalhoService:
    # Regras de negócio das ordens de trabalho e das suas linhas.
    # Não tem SQL (isso é dos repositórios) nem print/input (isso é das views).
    # Os erros de validação são ValueError, com mensagens prontas a mostrar ao utilizador.

    def __init__(self, repo_ot, repo_linha):
        self.repo_ot = repo_ot
        self.repo_linha = repo_linha

    # ---------- Validações auxiliares ----------

    # Garante que a data está no formato AAAA-MM-DD (com zeros), para as
    # comparações e pesquisas por data funcionarem
    def _validar_data(self, texto, nome_campo):
        try:
            data = datetime.strptime(texto, "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValueError(nome_campo + " inválida (usar AAAA-MM-DD): " + str(texto))
        if data.strftime("%Y-%m-%d") != texto:
            raise ValueError(nome_campo + " inválida (usar AAAA-MM-DD): " + str(texto))

    def _obter_ot_existente(self, id_ot):
        ot = self.repo_ot.procurar_por_id(id_ot)
        if ot is None:
            raise ValueError("OT não encontrada: " + str(id_ot))
        return ot

    # Uma OT entregue já não pode ser alterada
    def _garantir_editavel(self, ot):
        if ot.estado == OrdemTrabalho.ESTADO_ENTREGUE:
            raise ValueError("A OT " + str(ot.id_ot)
                             + " já foi entregue e não pode ser alterada")

    # ---------- Ordens de trabalho ----------

    # RF03 + RF05: cria uma OT no estado Pendente, já com o técnico responsável.
    # Se a viatura ou o técnico não existirem, a base de dados recusa (chave estrangeira).
    def criar_ot(self, id_viatura, id_tecnico, data_entrada, data_prev_saida,
                 descricao_avaria):
        if id_viatura is None:
            raise ValueError("Tem de indicar a viatura")
        self._validar_data(data_entrada, "Data de entrada")
        self._validar_data(data_prev_saida, "Data prevista de saída")
        if data_prev_saida < data_entrada:
            raise ValueError("A data prevista de saída não pode ser anterior "
                             "à data de entrada")
        if descricao_avaria is None or descricao_avaria.strip() == "":
            raise ValueError("A descrição da avaria é obrigatória")

        ot = OrdemTrabalho(id_viatura, id_tecnico, data_entrada, data_prev_saida,
                           descricao_avaria.strip())
        return self.repo_ot.inserir(ot)

    # RF06: muda o estado. As mudanças são livres (ex.: voltar a Pendente se o
    # trabalho atrasar), com duas exceções:
    #   - só se pode entregar uma OT que esteja Concluída;
    #   - uma OT Entregue já não muda de estado.
    # A data de saída real só é preenchida quando a OT passa a Entregue
    # (se não for indicada, usa a data de hoje).
    def mudar_estado(self, id_ot, novo_estado, data_saida_real=None):
        ot = self._obter_ot_existente(id_ot)
        if novo_estado not in OrdemTrabalho.ESTADOS:
            raise ValueError("Estado inválido: " + str(novo_estado))
        if novo_estado == ot.estado:
            return ot
        self._garantir_editavel(ot)

        if novo_estado == OrdemTrabalho.ESTADO_ENTREGUE:
            if ot.estado != OrdemTrabalho.ESTADO_CONCLUIDA:
                raise ValueError("Só é possível entregar uma OT que esteja Concluída")
            if data_saida_real is None:
                data_saida_real = date.today().isoformat()
            self._validar_data(data_saida_real, "Data de saída real")
            if data_saida_real < ot.data_entrada[:10]:
                raise ValueError("A data de saída real não pode ser anterior "
                                 "à data de entrada")
            ot.estado = novo_estado
            ot.data_saida_real = data_saida_real
            self.repo_ot.atualizar(ot)
        else:
            self.repo_ot.mudar_estado(id_ot, novo_estado)
            ot.estado = novo_estado
        return ot

    # RF05: troca o técnico responsável
    def atribuir_tecnico(self, id_ot, id_tecnico):
        ot = self._obter_ot_existente(id_ot)
        self._garantir_editavel(ot)
        if id_tecnico is None:
            raise ValueError("Tem de indicar o técnico responsável")
        self.repo_ot.atribuir_tecnico(id_ot, id_tecnico)
        ot.id_tecnico = id_tecnico
        return ot

    # ---------- Linhas da OT ----------

    # RF04 + RF13: adiciona uma linha e recalcula o custo da OT.
    # Uma linha de peça tem de indicar a peça (rastreabilidade, RNF03);
    # uma linha de mão-de-obra não tem peça.
    def adicionar_linha(self, id_ot, tipo, descricao, quantidade, preco_unitario,
                        horas_trabalhadas=None, id_peca=None):
        ot = self._obter_ot_existente(id_ot)
        self._garantir_editavel(ot)

        if descricao is None or descricao.strip() == "":
            raise ValueError("A descrição da linha é obrigatória")
        if quantidade is None or quantidade <= 0:
            raise ValueError("A quantidade tem de ser maior que zero")
        if preco_unitario is None or preco_unitario < 0:
            raise ValueError("O preço unitário não pode ser negativo")
        if tipo == LinhaOT.TIPO_PECA and id_peca is None:
            raise ValueError("Uma linha de peça tem de indicar a peça usada")
        if tipo == LinhaOT.TIPO_MAO_OBRA and id_peca is not None:
            raise ValueError("Uma linha de mão-de-obra não pode ter peça")

        linha = LinhaOT(id_ot, tipo, descricao.strip(), quantidade, preco_unitario,
                        horas_trabalhadas=horas_trabalhadas, id_peca=id_peca)
        self.repo_linha.inserir(linha)
        self.recalcular_custo(id_ot)
        return linha

    # Remove uma linha e recalcula o custo da OT
    def remover_linha(self, id_linha):
        linha = self.repo_linha.procurar_por_id(id_linha)
        if linha is None:
            raise ValueError("Linha não encontrada: " + str(id_linha))
        ot = self._obter_ot_existente(linha.id_ot)
        self._garantir_editavel(ot)
        self.repo_linha.apagar(id_linha)
        self.recalcular_custo(linha.id_ot)

    # RF13: soma o valor de todas as linhas, guarda o total na OT e devolve-o
    def recalcular_custo(self, id_ot):
        total = 0
        for linha in self.repo_linha.listar_por_ot(id_ot):
            total = total + linha.subtotal()
        total = round(total, 2)
        self.repo_ot.atualizar_custo_total(id_ot, total)
        return total

    # ---------- Consultas ----------

    def obter_ot(self, id_ot):
        return self._obter_ot_existente(id_ot)

    def listar_linhas(self, id_ot):
        self._obter_ot_existente(id_ot)
        return self.repo_linha.listar_por_ot(id_ot)

    # RF14
    def listar_em_curso(self):
        return self.repo_ot.listar_em_curso()

    # RF07
    def historico_por_matricula(self, matricula):
        if matricula is None or matricula.strip() == "":
            raise ValueError("Tem de indicar a matrícula")
        return self.repo_ot.listar_por_matricula(matricula.strip())

    # RF12: filtros opcionais por data de entrada, estado e técnico
    def pesquisar_ots(self, data_inicio=None, data_fim=None, estado=None,
                      id_tecnico=None):
        if data_inicio is not None:
            self._validar_data(data_inicio, "Data de início")
        if data_fim is not None:
            self._validar_data(data_fim, "Data de fim")
        if data_inicio is not None and data_fim is not None and data_inicio > data_fim:
            raise ValueError("A data de início não pode ser posterior à data de fim")
        if estado is not None and estado not in OrdemTrabalho.ESTADOS:
            raise ValueError("Estado inválido: " + str(estado))
        return self.repo_ot.pesquisar(data_inicio, data_fim, estado, id_tecnico)