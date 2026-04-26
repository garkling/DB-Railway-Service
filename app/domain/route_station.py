from dataclasses import dataclass


@dataclass
class RouteStation:
    route_id: int
    station_code: str
    stop_order: int
