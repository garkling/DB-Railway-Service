from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Coach:
    train_number: str
    service_date: date
    coach_number: int
    coach_type: str
    seat_capacity: int
    has_air_conditioning: bool
    class_code: str
    owner_operator_code: str | None


@dataclass
class SeatingCoach:
    train_number: str
    service_date: date
    coach_number: int
    seat_arrangement: str


@dataclass
class SleepingCoach:
    train_number: str
    service_date: date
    coach_number: int
    number_of_compartments: int
    berths_per_compartment: int


@dataclass
class DiningCoach:
    train_number: str
    service_date: date
    coach_number: int
    number_of_tables: int
    menu_type: str | None


@dataclass
class LuggageVan:
    train_number: str
    service_date: date
    coach_number: int
    max_weight_kg: Decimal
    has_bicycle_rack: bool
