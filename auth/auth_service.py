from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
from config import settings
from utilities.utilities_view import UtilitiesView
import httpx


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
        token = await self.remote_token(username, password, ip)
        request.session.update({"token": token})
        if token:
            usuario = await self.remote_user(token)
            if usuario:
                request.session.update({"user": usuario["user"]})
                request.session.update({"nombre": usuario["nombre"]})
                request.session.update({"apellido": usuario["apellido"]})
                request.session.update({"rol": usuario["rol"]})
                request.session.update({"destino": usuario["destino"]})
                return True

    async def logout(self, request: Request) -> bool:
        await UtilitiesView.registrar(
            request.session,
            request.url.path,
            request.method,
        )

        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return await self.remote_user(token)

    async def remote_token(self, username, password, ip=None):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.AUTH_API}/token",
                    data={"username": username, "password": password, "ip": ip},
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-Service": settings.APP_NAME.lower(),
                    },
                    timeout=20.0,
                )
            except httpx.RequestError:
                return False

            if response.status_code == 200:
                token_data = response.json()
                return token_data["access_token"]

    async def remote_user(self, token):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.AUTH_API}/get_user_info",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Service": settings.APP_NAME.lower(),
                    },
                )
        except httpx.RequestError:
            return False
        if response.status_code != 200:
            return False

        return response.json()
