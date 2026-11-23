# autoXpert/auth.py  (novo ficheiro)
# Autenticação: palavras-passe com bcrypt e sessão com JWT.
# Os nomes (SECRET_KEY, PERFIS, registar_utilizador, autenticar, criar_token,
# validar_token) são os do PDF do professor. O rbac.py, o login no main.py e o log de
# alterações dos outros elementos do grupo importam exatamente estes nomes.
import datetime
import os
import secrets
import sqlite3

import bcrypt
import jwt

# Chave que assina os tokens. Vem da variável de ambiente AUTOXPERT_SECRET.
# Se não estiver definida, geramos uma aleatória em cada arranque, em vez de deixar uma
# chave escrita no código (ficava visível no GitHub e qualquer pessoa podia forjar um
# token de administrador). Consequência: as sessões não sobrevivem a fechar o programa.
SECRET_KEY = os.environ.get("AUTOXPERT_SECRET") or secrets.token_hex(32)

# Perfis disponíveis na oficina
PERFIS = ["administrador", "tecnico", "rececionista"]

# O bcrypt só lê os primeiros 72 bytes; recusamos maiores em vez de os cortar em silêncio
TAMANHO_MAXIMO_BYTES = 72


def registar_utilizador(conn, login: str, senha: str, perfil: str):
    """Regista utilizador com hash bcrypt na BD."""
    if perfil not in PERFIS:
        raise ValueError("Perfil inválido: " + str(perfil))
    dados = senha.encode("utf-8")
    if len(dados) > TAMANHO_MAXIMO_BYTES:
        raise ValueError("A palavra-passe é demasiado longa (máximo 72 bytes).")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(dados, salt)
    login = login.strip()
    if not login:
        raise ValueError("O nome de utilizador é obrigatório.")
    # "Ana" e "ana" são o mesmo login. Verificamos aqui (e não só na coluna UNIQUE)
    # para funcionar também nas bases de dados que já existem, sem mudar o schema.
    if conn.execute("SELECT 1 FROM utilizadores WHERE login = ? COLLATE NOCASE",
                    (login,)).fetchone() is not None:
        raise sqlite3.IntegrityError("Esse nome de utilizador já existe.")
    conn.execute(
        "INSERT INTO utilizadores (login, senha_hash, perfil) VALUES (?, ?, ?)",
        (login, hashed.decode("ascii"), perfil)
    )
    conn.commit()


def autenticar(conn, login: str, senha: str) -> dict | None:
    """Verifica credenciais. Retorna dados do utilizador ou None."""
    row = conn.execute(
        "SELECT login, senha_hash, perfil FROM utilizadores "
        "WHERE login = ? COLLATE NOCASE",
        (login.strip(),)
    ).fetchone()
    if row is None:
        # Gasta o mesmo tempo que uma verificação verdadeira, para não se descobrir
        # que logins existem só pelo tempo de resposta.
        bcrypt.checkpw(b"dummy", bcrypt.hashpw(b"dummy", bcrypt.gensalt(4)))
        return None
    hash_guardado = row["senha_hash"]
    if isinstance(hash_guardado, str):
        hash_guardado = hash_guardado.encode("ascii")
    dados = senha.encode("utf-8")
    if len(dados) > TAMANHO_MAXIMO_BYTES:
        return None
    try:
        correta = bcrypt.checkpw(dados, hash_guardado)
    except ValueError:  # hash corrompido na BD: nunca deixa entrar
        return None
    if not correta:
        return None
    return {"login": row["login"], "perfil": row["perfil"]}


def criar_token(login: str, perfil: str) -> str:
    agora = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": login, "perfil": perfil,
        "iat": agora,
        "exp": agora + datetime.timedelta(hours=8),
        "iss": "autoxpert",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def validar_token(token: str) -> dict:
    # Levanta jwt.ExpiredSignatureError / jwt.InvalidTokenError, que o rbac.py (PDF)
    # já trata e converte em PermissionError.
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"], issuer="autoxpert")
