from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from config import settings
from auth.auth_service import AuthService
from admin.custom_admin import CustomAdmin
import uvicorn
from contextlib import asynccontextmanager
from database.db import async_engine

# from docs_apps import docs_gen, docs_op, DocsAuthMiddleware
# from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    ...
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Solo otro servicio",
    docs_url=None,
    description="""
    Servicio Web + API
    """,
    version="0.1.0",
    contact={
        "name": "Simon Bierozko",
        "email": "simon.bierozko@gmail.com",
    },
    openapi_tags=[
        {
            "name": "info",
            "description": "Operaciones relacionadas a informacion basica de la API",
        },
    ],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://icia-monitoreo:{settings.APP_PORT}",
        f"http://localhost:{settings.APP_PORT}",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

"""app.mount("/documentacion", docs_gen)
app.mount("/documentacion-operadores", docs_op)
app.mount("/static", StaticFiles(directory="static"), name="static")"""


@app.get("/", include_in_schema=False)
async def redirect_to_admin():
    return RedirectResponse(url=f"/{settings.APP_NAME}")


admin = CustomAdmin(
    app,
    async_engine,
    authentication_backend=AuthService(settings.AUTH_KEY),
    templates_dir="templates/",
    logo_url=f"/static/img/{settings.APP_NAME}.ico",
    title=f"{settings.APP_NAME.title()}",
    base_url=f"/{settings.APP_NAME}",
    favicon_url=f"/static/img/{settings.APP_NAME}.ico",
)

# app.add_middleware(DocsAuthMiddleware)


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.RELOAD,
    )
