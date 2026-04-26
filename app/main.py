import segno
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.controllers import forms_controller, home, reports_controller
from app.controllers.api import api_router
from app.exceptions import register_exception_handlers


def _qr_data_uri(payload: str, scale: int = 4) -> str:
    """Return a base64 data URI of an SVG QR code for the given payload.

    Used as a Jinja2 filter to render per-ticket QR codes inside <img> tags
    on the boarding-pass template (purely cosmetic — payload doesn't have to
    resolve anywhere).
    """
    return segno.make(str(payload), error="m").svg_data_uri(
        scale=scale, dark="#0e3a5f", light="#ffffff", border=2,
    )


app = FastAPI(title="Railway Travel Classes and Facilities — HW3")

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(settings.TEMPLATE_DIR))
templates.env.filters["qr_data_uri"] = _qr_data_uri
app.state.templates = templates

app.include_router(home.router)
app.include_router(forms_controller.router)
app.include_router(reports_controller.router)
app.include_router(api_router, prefix="/api")

register_exception_handlers(app)
