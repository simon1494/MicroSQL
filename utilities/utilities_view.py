from starlette.requests import Request
from services.helios import HeliosService


class UtilitiesView:
    def _rol_habilitado(self, request: Request) -> bool:
        rol = request.session.get("rol").lower()
        return rol in self.roles_con_visibilidad

    async def _template_normal(self, params, request):
        return await self.templates.TemplateResponse(
            request,
            self.remote_url,
            params,
        )

    async def _template_errores(self, params, request):
        return await self.templates.TemplateResponse(
            request,
            self.errores_url,
            params,
        )

    def form_a_dict(self, form):
        return {field.name: field.data for field in form}

    async def registrar_actividad(
        self, datos_session, url, method, detalles=None, id_interno_servicio=None
    ):
        HeliosService.enviar(datos_session, url, method, detalles, id_interno_servicio)

    def tiene_acceso_superior_de_edicion(self, request):
        rol = request.session.get("rol").lower()

        return rol in ("administrador",)
