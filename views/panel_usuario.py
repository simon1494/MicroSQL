from wtforms import Form, StringField, PasswordField
from utilities.utilities_view import UtilitiesView
from sqladmin import BaseView, expose
from fastapi.responses import Response, JSONResponse
import httpx
from itsdangerous import URLSafeSerializer
from fastapi import Request, HTTPException, status
from services.cerberus import CerberusService


class DatosPersonalesForm(Form):
    email = StringField(
        "Nuevo Email",
        render_kw={
            "class": "form-control",
            "placeholder": "Dejar vacio si no se quiere modificar",
        },
    )

    telefono = StringField(
        "Nuevo telefono de contacto",
        render_kw={
            "class": "form-control",
            "placeholder": "Dejar vacio si no se quiere modificar",
        },
    )


class SeguridadForm(Form):
    actual = PasswordField(
        "Contraseña actual",
        render_kw={
            "class": "form-control",
        },
    )

    nueva1 = PasswordField(
        "Contraseña nueva",
        render_kw={"class": "form-control"},
    )

    nueva2 = PasswordField(
        "Repita nueva",
        render_kw={"class": "form-control"},
    )


class DatosPersonalesView(BaseView, UtilitiesView):
    identity = "datos_personales"
    name = "datos_personales"
    name_plural = "datos_personales"
    remote_url = "sqladmin/cambiar-datos.html"
    errores_url = "sqladmin/cambiar-datos-error.html"

    @expose("/datos-personales", methods=["GET", "POST"])
    async def datos_personales(self, request):
        formu = DatosPersonalesForm()
        datos = await CerberusService.get_datos_usuario(request)
        params = {
            "title": "Modificar datos personales",
            "form": formu,
            "csrf_token": self.generar_csrf_token(request),
            "datos_actuales": datos,
        }
        match request.method:
            case "GET":
                request.session.update({"csrf_token": params["csrf_token"]})

                return await self._template_normal(params, request)
            case "POST":
                saved_token = request.session.get("csrf_token")
                form = self.procesar_form(await request.form())
                token = form["csrf_token"]
                if not saved_token or saved_token != token:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="CSRF inválido. Debe recargar el formulario de envio.",
                    )

                request.session.update({"csrf_token": ""})
                try:
                    user_data = {
                        "email": form["email"],
                        "telefono": form["telefono"],
                    }
                    resultado = await CerberusService.update_user_data(
                        request, user_data
                    )

                    if resultado:
                        # Registrar actividad exitosa
                        await self.registrar_actividad(
                            request.session,
                            request.url.path,
                            request.method,
                        )
                        return Response(status_code=200)
                    return Response(status_code=400)

                except ValueError:
                    return Response(status_code=500)
                except httpx.RequestError:
                    return Response(status_code=500)
                except Exception:
                    return Response(status_code=505)

    def generar_csrf_token(self, request: Request):
        import time
        import secrets

        SECRET_KEY = "clave"
        serializer = URLSafeSerializer(SECRET_KEY)

        # Generar un valor único que cambie en cada llamada
        unique_value = f"{request.client.host}_{time.time()}_{secrets.token_hex(8)}"

        token = serializer.dumps(unique_value)
        return token

    def procesar_form(self, form_raw):
        form_dict = {}
        for k, v in form_raw.multi_items():
            form_dict.setdefault(k, v)
        return form_dict

    def is_visible(self, request):
        return False


class SeguridadView(BaseView, UtilitiesView):
    identity = "seguridad"
    name = "seguridad"
    name_plural = "seguridad"
    remote_url = "sqladmin/cambiar-passw.html"

    @expose("/cambiar-passw", methods=["GET", "POST"])
    async def cambiar_passw(self, request):
        formu = SeguridadForm()
        params = {
            "title": "Modificar contraseña",
            "form": formu,
            "csrf_token": self.generar_csrf_token(request),
        }

        match request.method:
            case "GET":
                request.session.update({"csrf_token": params["csrf_token"]})
                return await self._template_normal(params, request)
            case "POST":
                saved_token = request.session.get("csrf_token")
                form = self.procesar_form(await request.form())
                token = form["csrf_token"]
                if not saved_token or saved_token != token:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content="CSRF Token invalido",
                    )

                try:
                    if form["nueva1"] != form["nueva2"]:
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content="Las contraseñas nuevas no coinciden",
                        )

                    user_passw = {
                        "old_passw": form["actual"],
                        "passw": form["nueva1"],
                    }
                    resultado = await CerberusService.update_user_passw(
                        request, user_passw
                    )

                    request.session.update({"csrf_token": ""})
                    match resultado.status_code:
                        case 201:
                            # Registrar actividad exitosa
                            await self.registrar_actividad(
                                request.session,
                                request.url.path,
                                request.method,
                            )
                            return Response(status_code=201)
                        case 400:
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content="Datos inválidos",
                            )
                        case 401:
                            return JSONResponse(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                content="La contraseña actual ingresada no es correcta",
                            )
                        case _:
                            return JSONResponse(
                                status_code=resultado.status_code,
                                content="Error al actualizar contraseña.",
                            )
                except Exception as e:
                    raise e

    def generar_csrf_token(self, request: Request):
        import time
        import secrets

        SECRET_KEY = "clave"
        serializer = URLSafeSerializer(SECRET_KEY)

        # Generar un valor único que cambie en cada llamada
        unique_value = f"{request.client.host}_{time.time()}_{secrets.token_hex(8)}"

        token = serializer.dumps(unique_value)
        return token

    def procesar_form(self, form_raw):
        form_dict = {}
        for k, v in form_raw.multi_items():
            form_dict.setdefault(k, v)
        return form_dict

    def is_visible(self, request):
        return False
