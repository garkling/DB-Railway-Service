from dataclasses import dataclass


@dataclass
class Facility:
    facility_id: int
    facility_name: str
    facility_description: str | None
