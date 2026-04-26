from dataclasses import dataclass


@dataclass
class Station:
    station_code: str
    station_name: str
    city: str
    country: str
    number_of_platforms: int | None
