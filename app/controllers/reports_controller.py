from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse

from app.dependencies import (
    get_boarding_pass_service,
    get_lookup_service,
    get_manifest_service,
    get_pricing_service,
)
from app.services.boarding_pass_service import BoardingPassService
from app.services.lookup_service import LookupService
from app.services.manifest_service import TrainManifestService
from app.services.pricing_service import RoutePricingService

router = APIRouter(tags=["reports"])


@router.get("/reports/boarding-pass", response_class=HTMLResponse)
def boarding_pass_report(
    request: Request,
    train: str | None = Query(None),
    service_date: date | None = Query(None, alias="date"),
    ticket: int | None = Query(None),
    bp_svc: BoardingPassService = Depends(get_boarding_pass_service),
    lookup: LookupService = Depends(get_lookup_service),
) -> HTMLResponse:
    boarding_pass = None
    if train and service_date and ticket:
        boarding_pass = bp_svc.build(train, service_date, ticket)

    return request.app.state.templates.TemplateResponse(
        request,
        "reports/boarding_pass.html",
        {
            "trains": lookup.trains_with_tickets_for_dropdown(),
            "boarding_pass": boarding_pass,
            "values": {
                "train": train or "",
                "service_date": service_date.isoformat() if service_date else "",
                "ticket": ticket if ticket is not None else "",
            },
        },
    )


@router.get("/reports/train-manifest", response_class=HTMLResponse)
def train_manifest_report(
    request: Request,
    train: str | None = Query(None),
    service_date: date | None = Query(None, alias="date"),
    manifest_svc: TrainManifestService = Depends(get_manifest_service),
    lookup: LookupService = Depends(get_lookup_service),
) -> HTMLResponse:
    manifest = None
    if train and service_date:
        manifest = manifest_svc.build(train, service_date)

    return request.app.state.templates.TemplateResponse(
        request,
        "reports/train_manifest.html",
        {
            "trains": lookup.trains_for_dropdown(),
            "manifest": manifest,
            "values": {
                "train": train or "",
                "service_date": service_date.isoformat() if service_date else "",
            },
        },
    )


@router.get("/reports/route-pricing", response_class=HTMLResponse)
def route_pricing_report(
    request: Request,
    operator: str | None = Query(None),
    route: int | None = Query(None),
    pricing_svc: RoutePricingService = Depends(get_pricing_service),
    lookup: LookupService = Depends(get_lookup_service),
) -> HTMLResponse:
    operator_filter = operator if operator else None
    route_filter = route if route is not None else None
    schedule = pricing_svc.build(
        operator_filter=operator_filter, route_filter=route_filter,
    )

    return request.app.state.templates.TemplateResponse(
        request,
        "reports/route_pricing.html",
        {
            "operators": lookup.operators_for_dropdown(),
            "routes": lookup.routes_for_dropdown(),
            "schedule": schedule,
            "values": {
                "operator": operator or "",
                "route": str(route) if route is not None else "",
            },
        },
    )
