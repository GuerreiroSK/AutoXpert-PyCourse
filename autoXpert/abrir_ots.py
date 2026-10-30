import tkinter as tk

from db.connection import inicializar_bd, get_connection
from src.repositories.ot_repository import OrdemTrabalhoRepository
from src.repositories.linha_ot_repository import LinhaOTRepository
from src.services.ot_service import OrdemTrabalhoService
from src.services.linha_ot_service import LinhaOTService
from src.controllers.ot_controller import OrdemTrabalhoController
from src.controllers.linha_ot_controller import LinhaOTController
from src.views.ot_view import JanelaOTs


# Abre a janela das Ordens de Trabalho.
# Liga as camadas de baixo para cima: ligação -> repositórios -> services -> controllers -> view.
if __name__ == "__main__":
    inicializar_bd()  # Cria as tabelas que ainda não existam

    conexao = get_connection()
    repo_ot = OrdemTrabalhoRepository(conexao)
    repo_linha = LinhaOTRepository(conexao)

    # O service das linhas usa o service das OTs (para validar a OT e guardar o custo)
    ot_service = OrdemTrabalhoService(repo_ot)
    linha_service = LinhaOTService(repo_linha, ot_service)

    ot_controller = OrdemTrabalhoController(ot_service)
    linha_controller = LinhaOTController(linha_service)

    raiz = tk.Tk()
    JanelaOTs(raiz, ot_controller, linha_controller)
    raiz.mainloop()

    conexao.close()
