from db.connection import inicializar_bd, get_connection


if __name__ == "__main__":
    inicializar_bd()  # Cria as tabelas que ainda não existam

    with get_connection() as conn:
        print("Ligação à base de dados estabelecida!")