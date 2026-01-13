from starlette.requests import Request
from functools import wraps
from fastapi import HTTPException, status


def get_original_ip(request: Request):
    h = request.headers
    return (
        h.get("x-real-ip")
        or (
            h.get("x-forwarded-for", "").split(",")[0].strip()
            if h.get("x-forwarded-for")
            else None
        )
        or request.client.host
    )


def roles_habilitados(*roles_permitidos):
    roles_permitidos = [r.lower() for r in roles_permitidos]

    def decorator(func):
        @wraps(func)
        async def wrapper(self, request: Request, *args, **kwargs):
            rol = request.session.get("rol", "").lower()
            if rol not in roles_permitidos:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Su rol no posee permisos suficientes acceder a este apartado",
                )
            return await func(self, request, *args, **kwargs)

        return wrapper

    return decorator


def destinos_restringidos(*destinos):
    destinos = [r.lower() for r in destinos]

    def decorator(func):
        @wraps(func)
        async def wrapper(self, request: Request, *args, **kwargs):
            contiene = lambda t, l: any(t in s for s in l)
            destino = request.session.get("destino", "").lower()
            if contiene(destino, destinos):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No dispone de permisos para acceder a este apartado.",
                )
            return await func(self, request, *args, **kwargs)

        return wrapper

    return decorator
