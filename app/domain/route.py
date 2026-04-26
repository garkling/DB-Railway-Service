from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Route:
    route_id: int
    route_name: str
    total_distance_km: Decimal | None
    distance_price_multiplier: Decimal | None = None
