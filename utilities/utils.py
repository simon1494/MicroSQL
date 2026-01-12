from starlette.requests import Request


def get_original_ip(request: Request):
    h = request.headers
    return (
        h.get("x-real-ip")
        or (
            h.get("x-forwarded-for", "").split(",")[0].strip()
            if h.get("x-forwarded-for")
            else None
        )
        or request.client.host
    )
