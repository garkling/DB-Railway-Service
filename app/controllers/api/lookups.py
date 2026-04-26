from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import get_lookup_service
from app.dto.responses import TicketResponse
from app.services.lookup_service import LookupService

router = APIRouter()


@router.get(
    "/tickets-for-train/{train_number}/{service_date}",
    response_model=list[TicketResponse],
)
def tickets_for_train(
    train_number: str,
    service_date: date,
    lookup: LookupService = Depends(get_lookup_service),
) -> list[TicketResponse]:
    tickets = lookup.tickets_for_train(train_number, service_date)
    return [TicketResponse.from_domain(t) for t in tickets]