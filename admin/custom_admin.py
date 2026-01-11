from sqladmin import Admin
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine


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
