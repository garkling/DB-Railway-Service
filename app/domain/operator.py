from dataclasses import dataclass
from decimal import Decimal


@dataclass
class RailwayOperator:
    operator_code: str
    operator_name: str
    country: str
    contact_phone: str | None
    base_fare: Decimal
