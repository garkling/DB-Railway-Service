from datetime import date

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_ticket_service
from app.dto.responses import TicketResponse
from app.dto.ticket_dto import IssueTicketDTO
from app.services.commands import CancelTicketCommand, IssueTicketCommand
from app.services.ticket_service import TicketService

router = APIRouter()


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def issue_ticket_api(
    dto: IssueTicketDTO,
    svc: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    cmd = IssueTicketCommand(
        train_number=dto.train_number,
        service_date=dto.service_date,
        passenger_id=dto.passenger_id,
        class_code=dto.class_code,
        seat_number=dto.seat_number,
        booking_date=dto.booking_date or date.today(),
    )
    ticket = svc.issue_ticket(cmd)
    return TicketResponse.from_domain(ticket)


@router.delete(
    "/{train_number}/{service_date}/{ticket_number}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def cancel_ticket_api(
    train_number: str,
    service_date: date,
    ticket_number: int,
    svc: TicketService = Depends(get_ticket_service),
) -> Response:
    cmd = CancelTicketCommand(
        train_number=train_number,
        service_date=service_date,
        ticket_number=ticket_number,
    )
    svc.cancel_ticket(cmd)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
