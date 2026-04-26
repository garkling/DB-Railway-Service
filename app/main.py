from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.controllers import forms_controller, home, reports_controller
from app.controllers.api import api_router
from app.exceptions import register_exception_handlers

app = FastAPI(title="Railway Travel Classes and Facilities — HW3")

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(settings.TEMPLATE_DIR))
app.state.templates = templates

app.include_router(home.router)
app.include_router(forms_controller.router)
app.include_router(reports_controller.router)
app.include_router(api_router, prefix="/api")

register_exception_handlers(app)
