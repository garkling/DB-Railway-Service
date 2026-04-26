from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class RescheduleTrainDTO(BaseModel):
    new_train_number: str = Field(min_length=1, max_length=10)
    new_service_date: date
    new_scheduled_departure: datetime
    new_scheduled_arrival: datetime

    @model_validator(mode="after")
    def _arrival_after_departure(self) -> "RescheduleTrainDTO":
        if self.new_scheduled_arrival <= self.new_scheduled_departure:
            raise ValueError(
                "new_scheduled_arrival must be strictly after new_scheduled_departure"
            )
        return self
