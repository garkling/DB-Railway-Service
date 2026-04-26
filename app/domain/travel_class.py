from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

BerthType = Literal["upper", "lower", "both"]


@dataclass
class TravelClass:
    class_code: str
    class_name: str
    description: str | None
    base_price_multiplier: Decimal


@dataclass
class FirstClass:
    class_code: str
    lounge_access: bool
    complimentary_meal: bool


@dataclass
class SecondClass:
    class_code: str
    has_folding_table: bool


@dataclass
class SleepingClass:
    class_code: str
    berth_type: str
    linens_included: bool
    compartment_capacity: int
