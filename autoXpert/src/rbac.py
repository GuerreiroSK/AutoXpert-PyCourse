
from functools import wraps

import jwt

from auth import validar_token


def obter_perfil(token):
    """Valida o token e devolve o perfil do utilizador."""

    if not token:
        raise PermissionError("Sessão não autenticada.")

    try:
        payload = validar_token(token)

    except jwt.ExpiredSignatureError:
        raise PermissionError("Sessão expirada.")

    except jwt.InvalidTokenError:
        raise PermissionError("Token inválido.")

    return payload.get("perfil")


def require_perfil(*perfis_permitidos):
    """
    Decorador que valida o JWT e verifica as permissões
    do utilizador antes de executar um método de um controller.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            perfil = obter_perfil(getattr(self, "token", None))

            if perfil not in perfis_permitidos:
                raise PermissionError(
                    f"Sem permissão. Perfis autorizados: {perfis_permitidos}"
                )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator

