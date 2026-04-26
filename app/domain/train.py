from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

TrainStatus = Literal["on_time", "delayed", "cancelled"]


@dataclass
class Train:
    train_number: str
    service_date: date
    scheduled_departure: datetime
    scheduled_arrival: datetime
    train_status: str
    operator_code: str
    route_id: int
    actual_departure: datetime | None = None
    actual_arrival: datetime | None = None
    delay_reason: str | None = None
    duration_minutes: int | None = None
