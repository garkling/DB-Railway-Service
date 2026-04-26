from dataclasses import dataclass
from decimal import Decimal


@dataclass
class OperatorClassRoutePricing:
    operator_code: str
    class_code: str
    route_id: int
    base_price: Decimal
