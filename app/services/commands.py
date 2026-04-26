from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.dto.ticket_dto import CancelTicketDTO
    from app.dto.train_dto import RescheduleTrainDTO


@dataclass(frozen=True)
class IssueTicketCommand:
    train_number: str
    service_date: date
    passenger_id: str
    class_code: str
    seat_number: str | None
    booking_date: date


@dataclass(frozen=True)
class CancelTicketCommand:
    train_number: str
    service_date: date
    ticket_number: int

    @classmethod
    def from_dto(cls, dto: "CancelTicketDTO") -> "CancelTicketCommand":
        return cls(
            train_number=dto.train_number,
            service_date=dto.service_date,
            ticket_number=dto.ticket_number,
        )


@dataclass(frozen=True)
class RescheduleTrainCommand:
    current_train_number: str
    current_service_date: date
    new_train_number: str
    new_service_date: date
    new_scheduled_departure: datetime
    new_scheduled_arrival: datetime

    @classmethod
    def from_dto(
        cls,
        dto: "RescheduleTrainDTO",
        current_train_number: str,
        current_service_date: date,
    ) -> "RescheduleTrainCommand":
        return cls(
            current_train_number=current_train_number,
            current_service_date=current_service_date,
            new_train_number=dto.new_train_number,
            new_service_date=dto.new_service_date,
            new_scheduled_departure=dto.new_scheduled_departure,
            new_scheduled_arrival=dto.new_scheduled_arrival,
        )
