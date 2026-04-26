from datetime import date

from pydantic import BaseModel, Field, field_validator


class CancelTicketDTO(BaseModel):
    train_number: str = Field(min_length=1, max_length=10)
    service_date: date
    ticket_number: int = Field(ge=1)


class IssueTicketDTO(BaseModel):
    train_number: str = Field(min_length=1, max_length=10)
    service_date: date
    passenger_id: str = Field(min_length=1, max_length=20)
    class_code: str = Field(min_length=1, max_length=5)
    seat_number: str | None = Field(default=None, max_length=10)
    booking_date: date | None = None

    @field_validator("seat_number")
    @classmethod
    def normalize_seat(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().upper()
        return v or None
