import httpx
from config import settings
from utilities.utils import get_original_ip
from fastapi import HTTPException, status
from fastapi.responses import Response, JSONResponse


class CerberusService:
    @staticmethod
    async def remote_token(username, password, ip=None):
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

    @staticmethod
    async def remote_user(token):
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

    @staticmethod
    async def ip_habilitada(request):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.AUTH_API}/estado-ip",
                    params={"ip": get_original_ip(request)},
                )
        except httpx.RequestError:
            return False

        data = response.json()
        habilitada = data.get("estado")
        restantes = data.get("restantes")
        return habilitada, restantes

    @staticmethod
    async def sumar_intento_fallido(request):
        # Fiscaliza el intento llamando al endpoint asincrónicamente (POST)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.AUTH_API}/sumar-fallido",
                params={"ip": get_original_ip(request)},
            )
            data = resp.json()
            habilitada = data.get("estado", 0)
            restantes = data.get("restantes", 0)
            return habilitada, restantes

    @staticmethod
    async def get_datos_usuario(request):
        url = f"{settings.AUTH_API}/get_user_info"
        token = request.session.get("token")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Service": "ariadna",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token inválido o expirado",
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error al obtener datos del usuario: {response.text}",
                    )

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error de conexión con el servicio de autenticación: {str(e)}",
            )

    @staticmethod
    async def update_user_data(request, user_data: dict):
        url = f"{settings.AUTH_API}/update-user-data"
        token = request.session.get("token")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    json=user_data,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Service": "ariadna",
                    },
                    timeout=10.0,
                )
                if response.status_code == 204:
                    return True
                elif response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token inválido o expirado",
                    )
                elif response.status_code == 400:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Datos inválidos: {response.json().get('detail', response.text)}",
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error al actualizar datos del usuario: {response.text}",
                    )

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error de conexión con el servicio de autenticación: {str(e)}",
            )

    @staticmethod
    async def update_user_passw(request, user_passw: dict):
        url = f"{settings.AUTH_API}/update-user-passw"
        token = request.session.get("token")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    json=user_passw,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Service": "ariadna",
                    },
                    timeout=10.0,
                )

                if response.status_code == 201:
                    return JSONResponse(
                        status_code=status.HTTP_201_CREATED,
                        content="Datos modificados correctamente.",
                    )
                elif response.status_code == 401:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content="La contraseña actual ingresada no es correcta",
                    )
                elif response.status_code == 400:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content=f"Datos inválidos: {response.json().get('detail', response.text)}",
                    )
                else:
                    return JSONResponse(
                        status_code=response.status_code,
                        content=f"Error al actualizar contraseña: {response.text}",
                    )

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error de conexión con el servicio de autenticación: {str(e)}",
            )
