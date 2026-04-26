from fastapi import APIRouter

from app.controllers.api import lookups, reports, tickets, trains

api_router = APIRouter()
api_router.include_router(tickets.router, prefix="/tickets", tags=["api-tickets"])
api_router.include_router(trains.router, prefix="/trains", tags=["api-trains"])
api_router.include_router(lookups.router, prefix="/lookups", tags=["api-lookups"])
api_router.include_router(reports.router, prefix="/reports", tags=["api-reports"])
