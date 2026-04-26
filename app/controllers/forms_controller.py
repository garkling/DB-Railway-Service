from datetime import date, datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError as PydanticValidationError

from app.dependencies import (
    get_lookup_service,
    get_ticket_service,
    get_train_service,
)
from app.dto.ticket_dto import CancelTicketDTO, IssueTicketDTO
from app.dto.train_dto import RescheduleTrainDTO
from app.services.commands import (
    CancelTicketCommand,
    IssueTicketCommand,
    RescheduleTrainCommand,
)
from app.services.lookup_service import LookupService
from app.services.ticket_service import TicketService
from app.services.train_service import TrainService

router = APIRouter(tags=["forms"])


@router.get("/forms/issue-ticket", response_class=HTMLResponse)
def issue_ticket_form(
    request: Request,
    lookup: LookupService = Depends(get_lookup_service),
) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(
        request,
        "forms/issue_ticket.html",
        {
            "trains": lookup.trains_for_dropdown(),
            "passengers": lookup.passengers_for_dropdown(),
            "classes": lookup.travel_classes(),
            "errors": None,
            "values": {},
        },
    )


@router.post("/forms/issue-ticket", response_class=HTMLResponse)
def issue_ticket_submit(
    request: Request,
    train_number: str = Form(...),
    service_date: date = Form(...),
    passenger_id: str = Form(...),
    class_code: str = Form(...),
    seat_number: str | None = Form(None),
    svc: TicketService = Depends(get_ticket_service),
    lookup: LookupService = Depends(get_lookup_service),
) -> HTMLResponse:
    raw_values = {
        "train_number": train_number,
        "service_date": service_date,
        "passenger_id": passenger_id,
        "class_code": class_code,
        "seat_number": seat_number,
    }
    try:
        dto = IssueTicketDTO(**raw_values)
    except PydanticValidationError as e:
        return request.app.state.templates.TemplateResponse(
            request,
            "forms/issue_ticket.html",
            {
                "trains": lookup.trains_for_dropdown(),
                "passengers": lookup.passengers_for_dropdown(),
                "classes": lookup.travel_classes(),
                "errors": e.errors(),
                "values": raw_values,
            },
            status_code=400,
        )

    cmd = IssueTicketCommand(
        train_number=dto.train_number,
        service_date=dto.service_date,
        passenger_id=dto.passenger_id,
        class_code=dto.class_code,
        seat_number=dto.seat_number,
        booking_date=dto.booking_date or date.today(),
    )
    ticket = svc.issue_ticket(cmd)
    snapshot = svc.list_tickets_for_train(ticket.train_number, ticket.service_date)

    return request.app.state.templates.TemplateResponse(
        request,
        "forms/issue_ticket_success.html",
        {
            "ticket": ticket,
            "tickets_snapshot": snapshot,
        },
    )


@router.get("/forms/reschedule-train", response_class=HTMLResponse)
def reschedule_train_form(
    request: Request,
    lookup: LookupService = Depends(get_lookup_service),
) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(
        request,
        "forms/reschedule_train.html",
        {
            "trains": lookup.trains_for_dropdown(),
            "errors": None,
            "values": {},
        },
    )


@router.post("/forms/reschedule-train", response_class=HTMLResponse)
def reschedule_train_submit(
    request: Request,
    current_train_number: str = Form(...),
    current_service_date: date = Form(...),
    new_train_number: str = Form(...),
    new_service_date: date = Form(...),
    new_scheduled_departure: datetime = Form(...),
    new_scheduled_arrival: datetime = Form(...),
    svc: TrainService = Depends(get_train_service),
    lookup: LookupService = Depends(get_lookup_service),
) -> HTMLResponse:
    raw_values = {
        "current_train_number": current_train_number,
        "current_service_date": current_service_date,
        "new_train_number": new_train_number,
        "new_service_date": new_service_date,
        "new_scheduled_departure": new_scheduled_departure,
        "new_scheduled_arrival": new_scheduled_arrival,
    }
    try:
        dto = RescheduleTrainDTO(
            new_train_number=new_train_number,
            new_service_date=new_service_date,
            new_scheduled_departure=new_scheduled_departure,
            new_scheduled_arrival=new_scheduled_arrival,
        )
    except PydanticValidationError as e:
        return request.app.state.templates.TemplateResponse(
            request,
            "forms/reschedule_train.html",
            {
                "trains": lookup.trains_for_dropdown(),
                "errors": e.errors(),
                "values": raw_values,
            },
            status_code=400,
        )

    cmd = RescheduleTrainCommand.from_dto(
        dto,
        current_train_number=current_train_number,
        current_service_date=current_service_date,
    )
    result = svc.reschedule_train(cmd)

    return request.app.state.templates.TemplateResponse(
        request,
        "forms/reschedule_train_success.html",
        {"result": result},
    )


@router.get("/forms/cancel-ticket", response_class=HTMLResponse)
def cancel_ticket_form(
    request: Request,
    lookup: LookupService = Depends(get_lookup_service),
) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(
        request,
        "forms/cancel_ticket.html",
        {
            "trains": lookup.trains_with_tickets_for_dropdown(),
            "errors": None,
            "values": {},
        },
    )


@router.post("/forms/cancel-ticket", response_class=HTMLResponse)
def cancel_ticket_submit(
    request: Request,
    train_number: str = Form(...),
    service_date: date = Form(...),
    ticket_number: int = Form(...),
    svc: TicketService = Depends(get_ticket_service),
    lookup: LookupService = Depends(get_lookup_service),
) -> HTMLResponse:
    raw_values = {
        "train_number": train_number,
        "service_date": service_date,
        "ticket_number": ticket_number,
    }
    try:
        dto = CancelTicketDTO(**raw_values)
    except PydanticValidationError as e:
        return request.app.state.templates.TemplateResponse(
            request,
            "forms/cancel_ticket.html",
            {
                "trains": lookup.trains_with_tickets_for_dropdown(),
                "errors": e.errors(),
                "values": raw_values,
            },
            status_code=400,
        )

    cmd = CancelTicketCommand.from_dto(dto)
    result = svc.cancel_ticket(cmd)

    return request.app.state.templates.TemplateResponse(
        request,
        "forms/cancel_ticket_success.html",
        {"result": result},
    )
