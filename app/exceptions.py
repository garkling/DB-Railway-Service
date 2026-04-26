from datetime import date as _date
from typing import TYPE_CHECKING

from fastapi import Request
from fastapi.responses import JSONResponse, Response

if TYPE_CHECKING:
    from fastapi import FastAPI


class DomainError(Exception):
    """Base class for all domain exceptions."""


class NotFoundError(DomainError):
    """A required entity does not exist."""


class PassengerNotFound(NotFoundError):
    def __init__(self, passenger_id: str):
        super().__init__(f"Passenger '{passenger_id}' does not exist")
        self.passenger_id = passenger_id


class TrainNotFound(NotFoundError):
    def __init__(self, train_number: str, service_date: _date):
        super().__init__(
            f"Train '{train_number}' on {service_date} does not exist"
        )
        self.train_number = train_number
        self.service_date = service_date


class TravelClassNotFound(NotFoundError):
    def __init__(self, class_code: str):
        super().__init__(f"Travel class '{class_code}' does not exist")
        self.class_code = class_code


class TicketNotFound(NotFoundError):
    def __init__(self, train_number: str, service_date: _date, ticket_number: int):
        super().__init__(
            f"Ticket {ticket_number} on train '{train_number}' "
            f"({service_date}) does not exist"
        )
        self.train_number = train_number
        self.service_date = service_date
        self.ticket_number = ticket_number


class ConflictError(DomainError):
    """The operation conflicts with current state."""


class PricingNotConfigured(ConflictError):
    def __init__(self, operator_code: str, class_code: str, route_id: int):
        super().__init__(
            f"No pricing configured for operator='{operator_code}', "
            f"class='{class_code}', route_id={route_id}"
        )
        self.operator_code = operator_code
        self.class_code = class_code
        self.route_id = route_id


class TrainAlreadyExists(ConflictError):
    def __init__(self, train_number: str, service_date: _date):
        super().__init__(
            f"Train '{train_number}' on {service_date} already exists"
        )
        self.train_number = train_number
        self.service_date = service_date


class ValidationError(DomainError):
    """Business-rule validation failure."""


def _render_error(
    request: Request, status_code: int, template: str, exc: Exception,
) -> Response:
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status_code,
            content={
                "error": exc.__class__.__name__,
                "message": str(exc),
            },
        )
    return request.app.state.templates.TemplateResponse(
        request,
        template,
        {
            "title": exc.__class__.__name__,
            "message": str(exc),
        },
        status_code=status_code,
    )


def register_exception_handlers(app: "FastAPI") -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(request: Request, exc: NotFoundError) -> Response:
        return _render_error(request, 404, "errors/not_found.html", exc)

    @app.exception_handler(ConflictError)
    async def _conflict(request: Request, exc: ConflictError) -> Response:
        return _render_error(request, 409, "errors/conflict.html", exc)

    @app.exception_handler(ValidationError)
    async def _validation(request: Request, exc: ValidationError) -> Response:
        return _render_error(request, 400, "errors/validation.html", exc)

    @app.exception_handler(DomainError)
    async def _domain_fallback(request: Request, exc: DomainError) -> Response:
        return _render_error(request, 422, "errors/server_error.html", exc)

    @app.exception_handler(Exception)
    async def _server_error(request: Request, exc: Exception) -> Response:
        return _render_error(request, 500, "errors/server_error.html", exc)
