from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

BookingStatus = Literal["confirmed", "cancelled", "refunded"]


@dataclass
class Ticket:
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
