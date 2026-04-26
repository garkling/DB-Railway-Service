from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.domain.reports import BoardingPass, RoutePricingSchedule, TrainManifest
    from app.domain.ticket import Ticket
    from app.domain.train import Train


class TicketResponse(BaseModel):
    train_number: str
    service_date: date
    ticket_number: int
    seat_number: str | None
    price_paid: Decimal
    booking_date: date
    passenger_id: str
    class_code: str
    booking_status: str
    payment_method: str

    @classmethod
    def from_domain(cls, ticket: "Ticket") -> "TicketResponse":
        return cls(**ticket.__dict__)


class TrainResponse(BaseModel):
    train_number: str
    service_date: date
    scheduled_departure: datetime
    scheduled_arrival: datetime
    train_status: str
    operator_code: str
    route_id: int
    actual_departure: datetime | None
    actual_arrival: datetime | None
    delay_reason: str | None
    duration_minutes: int | None

    @classmethod
    def from_domain(cls, train: "Train") -> "TrainResponse":
        return cls(**train.__dict__)


class RescheduleTrainResponse(BaseModel):
    train: TrainResponse
    coaches_cascaded: int
    tickets_cascaded: int


class BoardingPassResponse(BaseModel):
    ticket_number: int
    train_number: str
    service_date: date
    scheduled_departure: datetime
    scheduled_arrival: datetime
    operator_name: str
    passenger_full_name: str
    seat_number: str | None
    class_name: str
    class_description: str | None
    price_paid: Decimal
    booking_date: date
    origin_station: str | None
    destination_station: str | None

    @classmethod
    def from_domain(cls, bp: "BoardingPass") -> "BoardingPassResponse":
        return cls(**bp.__dict__)


class ManifestRowResponse(BaseModel):
    ticket_number: int
    seat_number: str | None
    passenger_id: str
    passenger_full_name: str
    class_code: str
    class_name: str
    price_paid: Decimal
    booking_date: date


class TrainManifestResponse(BaseModel):
    train_number: str
    service_date: date
    scheduled_departure: datetime
    scheduled_arrival: datetime
    operator_code: str
    operator_name: str
    route_id: int
    route_name: str
    total_passengers: int
    rows: list[ManifestRowResponse]

    @classmethod
    def from_domain(cls, m: "TrainManifest") -> "TrainManifestResponse":
        return cls(
            train_number=m.train_number,
            service_date=m.service_date,
            scheduled_departure=m.scheduled_departure,
            scheduled_arrival=m.scheduled_arrival,
            operator_code=m.operator_code,
            operator_name=m.operator_name,
            route_id=m.route_id,
            route_name=m.route_name,
            total_passengers=m.total_passengers,
            rows=[ManifestRowResponse(**r.__dict__) for r in m.rows],
        )


class PricingRowResponse(BaseModel):
    operator_code: str
    operator_name: str
    class_code: str
    class_name: str
    route_id: int
    route_name: str
    base_price: Decimal
    total_distance_km: Decimal | None
    distance_price_multiplier: Decimal | None


class RoutePricingScheduleResponse(BaseModel):
    rows: list[PricingRowResponse]
    operator_filter: str | None
    route_filter: int | None

    @classmethod
    def from_domain(
        cls, s: "RoutePricingSchedule",
    ) -> "RoutePricingScheduleResponse":
        return cls(
            rows=[PricingRowResponse(**r.__dict__) for r in s.rows],
            operator_filter=s.operator_filter,
            route_filter=s.route_filter,
        )
