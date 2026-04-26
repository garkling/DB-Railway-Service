from datetime import date as _date

from fastapi import APIRouter, Depends, Query

from app.dependencies import (
    get_boarding_pass_service,
    get_manifest_service,
    get_pricing_service,
)
from app.dto.responses import (
    BoardingPassResponse,
    RoutePricingScheduleResponse,
    TrainManifestResponse,
)
from app.services.boarding_pass_service import BoardingPassService
from app.services.manifest_service import TrainManifestService
from app.services.pricing_service import RoutePricingService

router = APIRouter()


@router.get("/boarding-pass", response_model=BoardingPassResponse)
def boarding_pass_api(
    train: str,
    service_date: _date = Query(..., alias="date"),
    ticket: int = Query(...),
    svc: BoardingPassService = Depends(get_boarding_pass_service),
) -> BoardingPassResponse:
    payload = svc.build(train, service_date, ticket)
    return BoardingPassResponse.from_domain(payload)


@router.get("/train-manifest", response_model=TrainManifestResponse)
def train_manifest_api(
    train: str,
    service_date: _date = Query(..., alias="date"),
    svc: TrainManifestService = Depends(get_manifest_service),
) -> TrainManifestResponse:
    payload = svc.build(train, service_date)
    return TrainManifestResponse.from_domain(payload)


@router.get("/route-pricing", response_model=RoutePricingScheduleResponse)
def route_pricing_api(
    operator: str | None = Query(None),
    route: int | None = Query(None),
    svc: RoutePricingService = Depends(get_pricing_service),
) -> RoutePricingScheduleResponse:
    operator_filter = operator if operator else None
    route_filter = route if route is not None else None
    payload = svc.build(
        operator_filter=operator_filter, route_filter=route_filter,
    )
    return RoutePricingScheduleResponse.from_domain(payload)
