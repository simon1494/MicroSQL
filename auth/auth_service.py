from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
from config import settings
from services.helios import HeliosService
from services.cerberus import CerberusService


class AuthService(AuthenticationBackend):
    def __init__(self, secret_key) -> None:
        super().__init__(secret_key)
        self.middlewares = [
            Middleware(
                SessionMiddleware,
                secret_key=secret_key,
                max_age=settings.SESSION_EXPIRE,
                same_site="lax",
                https_only=False,
                session_cookie=f"{settings.APP_NAME.lower()}_session",
            ),
        ]

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        ip = request.client.host
        token = await CerberusService.remote_token(username, password, ip)
        request.session.update({"token": token})
        if token:
            usuario = await CerberusService.remote_user(token)
            if usuario:
                request.session.update({"user": usuario["user"]})
                request.session.update({"nombre": usuario["nombre"]})
                request.session.update({"apellido": usuario["apellido"]})
                request.session.update({"rol": usuario["rol"]})
                request.session.update({"destino": usuario["destino"]})
                return True

    async def logout(self, request: Request) -> bool:
        HeliosService.enviar(
            request.session,
            request.url.path,
            request.method,
        )

        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return await CerberusService.remote_user(token)
