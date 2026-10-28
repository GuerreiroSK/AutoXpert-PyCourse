from src.models.cliente_models import Cliente
from db.connection import get_connection


class ClienteRepository:

    def inserir(self, cliente):
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO Cliente "
                "(nome, NIF, telefone, email, morada, data_registo) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    cliente.nome,
                    cliente.nif,
                    cliente.telefone,
                    cliente.email,
                    cliente.morada,
                    cliente.data_registo
                )
            )
            cliente.id_cliente = cur.lastrowid

        return cliente

    def listar_todos(self):
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM Cliente"
            ).fetchall()

        return [
            Cliente(
                nome=r["nome"],
                nif=r["NIF"],
                telefone=r["telefone"],
                email=r["email"],
                morada=r["morada"],
                data_registo=r["data_registo"],
                id_cliente=r["id_cliente"]
            )
            for r in rows
        ]