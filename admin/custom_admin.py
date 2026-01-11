from sqladmin import Admin
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.datastructures import URL
from typing import no_type_check
from sqladmin.helpers import get_object_identifier
from config import settings
import httpx
from services.helios import HeliosService


class CustomAdmin(Admin):
    def __init__(
        self,
        app: FastAPI,
        engine: AsyncEngine,
        authentication_backend,
        *,
        base_url: str = "/admin",
        templates_dir: str = None,
        title: str = "Admin",
        logo_url: str = None,
        favicon_url: str = None,
    ):
        super().__init__(
            app,
            engine,
            authentication_backend=authentication_backend,
            base_url=base_url,
            templates_dir=templates_dir,
            title=title,
            logo_url=logo_url,
            favicon_url=favicon_url,
        )

    async def login(self, request: Request) -> Response:
        assert self.authentication_backend is not None

        context = {}
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "sqladmin/login.html")

        habilitada, restantes = await self.ip_habilitada(request)
        if not habilitada:
            context["error"] = f"IP bloqueada - Reintente en {int(restantes)} minutos"
            return await self.templates.TemplateResponse(
                request, "sqladmin/login.html", context, status_code=400
            )

        ok = await self.authentication_backend.login(request)  # asd

        if not ok:
            # Obtiene la IP del usuario
            ip = self.get_original_ip(request)

            # Fiscaliza el intento llamando al endpoint asincrónicamente (POST)
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{settings.AUTH_API}/sumar-fallido",
                    params={"ip": ip},
                )
                data = resp.json()
                habilitada = data.get("estado", 0)
                restantes = data.get("restantes", 0)

            if habilitada:
                context["error"] = (
                    f"Credenciales inválidas - {restantes} intentos restantes"
                )
            else:
                context["error"] = (
                    f"IP bloqueada - Reintente en {f'{int(restantes)} minutos' if restantes >= 1 else 'unos momentos'}"
                )

            return await self.templates.TemplateResponse(
                request, "sqladmin/login.html", context, status_code=400
            )

        HeliosService.enviar(
            request.session,
            request.url.path,
            request.method,
        )

        return RedirectResponse(request.url_for("admin:index"), status_code=302)

    async def ip_habilitada(self, request):
        ip = self.get_original_ip(request)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.AUTH_API}/estado-ip",
                    params={"ip": ip},
                )
        except httpx.RequestError:
            return False

        data = response.json()
        habilitada = data.get("estado")
        restantes = data.get("restantes")
        return habilitada, restantes

    def get_original_ip(self, request: Request):
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

    def get_save_redirect_url(
        self, request: Request, form, model_view, obj
    ) -> str | URL:
        """
        Get the redirect URL after a save action
        which is triggered from create/edit page.
        """

        identity = request.path_params["identity"]
        identifier = get_object_identifier(obj)

        if form.get("save") == "Guardar":
            return request.url_for("admin:list", identity=identity)
        elif form.get("save") == "Guardar y continuar editando" or (
            form.get("save") == "Guardar como nuevo" and model_view.save_as_continue
        ):
            return request.url_for("admin:edit", identity=identity, pk=identifier)
        return request.url_for("admin:create", identity=identity)


def bare_expose(
    path: str,
    *,
    methods: list[str] = ["GET"],
    identity: str | None = None,
    include_in_schema: bool = True,
):
    """Expose View with information."""

    @no_type_check
    def wrap(func):
        func._exposed = True
        func._path = path
        func._methods = methods
        func._identity = identity or func.__name__
        func._include_in_schema = include_in_schema
        return func

    return wrap
