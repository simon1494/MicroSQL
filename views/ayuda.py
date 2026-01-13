from sqladmin import BaseView, expose
from fastapi.responses import (
    RedirectResponse,
)
from utilities.utilities_view import UtilitiesView
from utilities.utils import roles_habilitados


class AyudaView(BaseView, UtilitiesView):
    name = "Guia de Usuario"
    name_plural = "Guia de Usuario - Online"
    icon = "fa-solid fa-circle-info"
    category = "Centro de Ayuda"
    roles_con_visibilidad = (
        "administrador",
        "estrategico",
        "analista",
        "supervisor",
        "operador",
    )

    def is_visible(self, request) -> bool:
        """Check if user has the required role to see this view."""
        rol = request.session.get("rol", "").lower()
        return rol in [r.lower() for r in self.roles_con_visibilidad]

    @expose("/centro-de-ayuda", methods=["GET"])
    @roles_habilitados(*roles_con_visibilidad)
    async def redirigir_a_docs(self, request):
        match request.method:
            case "GET":
                rol = request.session.get("rol", "").lower()
                if rol == "operador":
                    return RedirectResponse(url="/documentacion-operadores")
                # return RedirectResponse(url="/documentacion")
                return RedirectResponse(url="/documentacion-operadores")


class ManualView(BaseView, UtilitiesView):
    name = "Guia PDF"
    name_plural = "Guia de Usuario - PDF"
    icon = "fa-solid fa-file-pdf"
    category = "Centro de Ayuda"
    roles_con_visibilidad = (
        "administrador",
        "estrategico",
        "supervisor",
        "operador",
        "analista",
    )

    def is_visible(self, request) -> bool:
        """Check if user has the required role to see this view."""
        rol = request.session.get("rol", "").lower()
        return rol in [r.lower() for r in self.roles_con_visibilidad]

    @expose("/guia-usuario-pdf", methods=["GET"])
    @roles_habilitados(*roles_con_visibilidad)
    async def ver_manual(self, request):
        match request.method:
            case "GET":
                await self.registrar_actividad(
                    request.session,
                    request.url.path,
                    request.method,
                    detalles={"Visualizacion Guia PDF"},
                )
                rol = request.session.get("rol", "").lower()
                if rol == "operador":
                    return RedirectResponse(url="/documentacion-operadores/op-pdf")
                # return RedirectResponse(url="/documentacion/gen-pdf")
                return RedirectResponse(url="/documentacion-operadores/op-pdf")
