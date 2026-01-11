from fastapi.responses import JSONResponse


class ExposedLogic:
    async def activo(self, request):
        usuario = request.session.get("user", "")
        respuesta = True if usuario != "" else False
        return JSONResponse(status_code=200, content=respuesta)
