from datetime import datetime


def on_config(config, **kwargs):
    """Guardar fecha de build en config.extra."""
    today = datetime.now().strftime("%d-%m-%Y")
    config.extra["build_date"] = today
    return config


def on_page_markdown(markdown, page, config, files, **kwargs):
    """Reemplazar marcador por la fecha de build en todos los .md."""
    build_date = config.extra.get("build_date", "")
    return markdown.replace("{{BUILD_DATE}}", build_date)
