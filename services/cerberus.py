import httpx
from config import settings


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
