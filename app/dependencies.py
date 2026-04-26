from fastapi import Depends
from sqlalchemy import Engine

from app.db import get_engine
from app.services.boarding_pass_service import BoardingPassService
from app.services.lookup_service import LookupService
from app.services.manifest_service import TrainManifestService
from app.services.pricing_service import RoutePricingService
from app.services.ticket_service import TicketService
from app.services.train_service import TrainService


def get_ticket_service(engine: Engine = Depends(get_engine)) -> TicketService:
    return TicketService(engine)


def get_lookup_service(engine: Engine = Depends(get_engine)) -> LookupService:
    return LookupService(engine)


def get_train_service(engine: Engine = Depends(get_engine)) -> TrainService:
    return TrainService(engine)


def get_boarding_pass_service(
    engine: Engine = Depends(get_engine),
) -> BoardingPassService:
    return BoardingPassService(engine)


def get_manifest_service(
    engine: Engine = Depends(get_engine),
) -> TrainManifestService:
    return TrainManifestService(engine)


def get_pricing_service(
    engine: Engine = Depends(get_engine),
) -> RoutePricingService:
    return RoutePricingService(engine)
