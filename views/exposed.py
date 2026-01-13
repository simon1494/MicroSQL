from sqladmin import BaseView
from admin.custom_admin import bare_expose
from starlette.requests import Request
from internal.exposed_logic import ExposedLogic


class ExposedView(BaseView, ExposedLogic):
    identity = "exposed"
    name = "exposed"

    @bare_expose("/activo", methods=["GET"])
    async def activo_endpoint(self, request):
        return await self.activo(request)

    def is_visible(self, request: Request) -> bool:
        return False
