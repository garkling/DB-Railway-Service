from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from app.domain.coach import Coach
from app.domain.ticket import Ticket
from app.domain.train import Train


@dataclass
class BoardingPass:
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


@dataclass
class ManifestRow:
    ticket_number: int
    seat_number: str | None
    passenger_id: str
    passenger_full_name: str
    class_code: str
    class_name: str
    price_paid: Decimal
    booking_date: date


@dataclass
class TrainManifest:
    train_number: str
    service_date: date
    scheduled_departure: datetime
    scheduled_arrival: datetime
    operator_code: str
    operator_name: str
    route_id: int
    route_name: str
    total_passengers: int
    rows: list[ManifestRow]


@dataclass
class PricingRow:
    operator_code: str
    operator_name: str
    class_code: str
    class_name: str
    route_id: int
    route_name: str
    base_price: Decimal
    total_distance_km: Decimal | None
    distance_price_multiplier: Decimal | None


@dataclass
class RoutePricingSchedule:
    rows: list[PricingRow]
    operator_filter: str | None = None
    route_filter: int | None = None


@dataclass
class TrainCascadeSnapshot:
    train: Train | None
    coaches: list[Coach]
    tickets: list[Ticket]


@dataclass
class RescheduleTrainResult:
    updated_train: Train
    before: TrainCascadeSnapshot
    after: TrainCascadeSnapshot


@dataclass
class CancelTicketResult:
    deleted_ticket: Ticket
    before_tickets: list[Ticket]
    after_tickets: list[Ticket]
