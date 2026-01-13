from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse
import httpx
from pathlib import Path
from fastapi.responses import FileResponse
from config import settings

BASE_DIR = Path(__file__).resolve().parent


docs_op = FastAPI()


@docs_op.get("/op-pdf")
def manual_op():
    pdf_path = (
        BASE_DIR
        / "docs"
        / "docs-op"
        / "site"
        / f"guia-{settings.APP_NAME.lower()}-op.pdf"
    )
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"guia-{settings.APP_NAME.lower()}-op.pdf",
    )


docs_op.mount(
    "/",
    StaticFiles(directory="./docs/docs-op/site", html=True),
    name="docs-op",
)

docs_gen = FastAPI()


@docs_gen.get("/gen-pdf")
def manual_gen():
    """pdf_path = BASE_DIR / "docs" / "docs-gen" / "site" / "guia-ariadna.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return FileResponse(
        pdf_path, media_type="application/pdf", filename="guia-ariadna.pdf"
    )"""

    pdf_path = (
        BASE_DIR / "docs" / "docs-op" / "site" / f"guia-{settings.APP_NAME.lower()}.pdf"
    )
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"guia-{settings.APP_NAME.lower()}.pdf",
    )


docs_gen.mount(
    "/",
    StaticFiles(directory="./docs/docs-gen/site", html=True),
    name="docs",
)


class DocsAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Solo verificar autenticación para rutas /docu
        if request.url.path.startswith("/documentacion"):
            try:
                # Construir la URL base del servidor actual
                base_url = f"{request.url.scheme}://{request.url.netloc}"
                check_url = f"{base_url}/{settings.APP_NAME.lower()}/activo"

                # Copiar las cookies del request original para enviarlas en la verificación
                cookies = request.cookies

                async with httpx.AsyncClient() as client:
                    response = await client.get(check_url, cookies=cookies, timeout=5.0)

                    if response.status_code == 200:
                        # Intentar parsear como JSON
                        try:
                            data = response.json()
                            if data is True or data == True:
                                response = await call_next(request)
                                return response
                        except Exception:
                            # Si no es JSON válido, verificar si el texto es "true"
                            if response.text.strip().lower() == "true":
                                response = await call_next(request)
                                return response

                    return RedirectResponse(url=f"/{settings.APP_NAME.lower()}/login")

            except httpx.RequestError:
                return RedirectResponse(url=f"/{settings.APP_NAME.lower()}/login")
            except HTTPException:
                return RedirectResponse(url=f"/{settings.APP_NAME.lower()}/login")
            except Exception as e:
                print(f"Error inesperado: {e}")
                return RedirectResponse(url=f"/{settings.APP_NAME.lower()}/login")

        response = await call_next(request)
        return response
