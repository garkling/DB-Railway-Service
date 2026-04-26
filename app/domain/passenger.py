from dataclasses import dataclass
from datetime import date


@dataclass
class Passenger:
    passenger_id: str
    first_name: str
    last_name: str
    date_of_birth: date | None
    email: str | None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
