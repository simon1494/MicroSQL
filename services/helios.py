import httpx
import asyncio
from config import settings


class HeliosService:
    @staticmethod
    def enviar(
        datos_usuario, ruta, metodo_http, detalles=None, id_interno_servicio=None
    ) -> None:
        """Dispara el webhook en segundo plano y no espera respuesta."""

        payload = {
            "user": datos_usuario.get("user"),
            "nombre": datos_usuario.get("nombre") or "",
            "apellido": datos_usuario.get("apellido") or "",
            "destino": datos_usuario.get("destino"),
            "rol": datos_usuario.get("rol"),
            "servicio": f"{settings.APP_NAME.title()}",
            "ruta": ruta,
            "metodo_http": metodo_http,
            "detalles": detalles or {},
            "id_interno_servicio": id_interno_servicio or None,
        }

        async def _task():
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{settings.HELIOS_API}/registrar-log",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=10.0,
                    )
            except Exception as e:
                print(e)
                pass

        if settings.DEVELOPMENT is False:
            asyncio.create_task(_task())
