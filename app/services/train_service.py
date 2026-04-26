from dataclasses import replace

from sqlalchemy import Engine

from app.domain.reports import RescheduleTrainResult, TrainCascadeSnapshot
from app.exceptions import TrainAlreadyExists, TrainNotFound, ValidationError
from app.repositories.coach_repository import CoachRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.train_repository import TrainRepository
from app.services.commands import RescheduleTrainCommand


class TrainService:
    def __init__(self, engine: Engine):
        self._engine = engine

    def reschedule_train(
        self, cmd: RescheduleTrainCommand,
    ) -> RescheduleTrainResult:
        """Reschedule a train; cascade UPDATE per APD-007 §2.

        9 SQL queries fire in order inside engine.begin():
          1. SELECT 1 FROM train WHERE current_pk LIMIT 1
          2. SELECT 1 FROM train WHERE new_pk LIMIT 1
          3. SELECT ... FROM train WHERE current_pk
          4. SELECT ... FROM coach WHERE current_pk
          5. SELECT ... FROM ticket WHERE current_pk
          6. UPDATE train SET ... WHERE current_pk  (FK cascades to coach + ticket)
          7. SELECT ... FROM train WHERE new_pk
          8. SELECT ... FROM coach WHERE new_pk
          9. SELECT ... FROM ticket WHERE new_pk
        """
        if cmd.new_scheduled_arrival <= cmd.new_scheduled_departure:
            raise ValidationError(
                "new_scheduled_arrival must be strictly after new_scheduled_departure"
            )

        with self._engine.begin() as conn:
            train_repo = TrainRepository(conn)
            coach_repo = CoachRepository(conn)
            ticket_repo = TicketRepository(conn)

            # 1. Existence check (current PK)
            if not train_repo.exists(cmd.current_train_number, cmd.current_service_date):
                raise TrainNotFound(cmd.current_train_number, cmd.current_service_date)

            # 2. Clash check (new PK) — only if new PK actually differs
            new_pk_differs = (
                cmd.new_train_number != cmd.current_train_number
                or cmd.new_service_date != cmd.current_service_date
            )
            if new_pk_differs and train_repo.exists(
                cmd.new_train_number, cmd.new_service_date,
            ):
                raise TrainAlreadyExists(cmd.new_train_number, cmd.new_service_date)

            # 3-5. Before snapshots (current PK)
            before_train = train_repo.get(cmd.current_train_number, cmd.current_service_date)
            before_coaches = coach_repo.list_for_train(
                cmd.current_train_number, cmd.current_service_date,
            )
            before_tickets = ticket_repo.list_for_train(
                cmd.current_train_number, cmd.current_service_date,
            )

            # 6. Cascade UPDATE — preserves status / operator / route / actual_* / delay_reason
            new_state = replace(
                before_train,
                train_number=cmd.new_train_number,
                service_date=cmd.new_service_date,
                scheduled_departure=cmd.new_scheduled_departure,
                scheduled_arrival=cmd.new_scheduled_arrival,
            )
            train_repo.update(
                cmd.current_train_number, cmd.current_service_date, new_state,
            )

            # 7-9. After snapshots (new PK)
            after_train = train_repo.get(cmd.new_train_number, cmd.new_service_date)
            after_coaches = coach_repo.list_for_train(
                cmd.new_train_number, cmd.new_service_date,
            )
            after_tickets = ticket_repo.list_for_train(
                cmd.new_train_number, cmd.new_service_date,
            )

            return RescheduleTrainResult(
                updated_train=after_train,
                before=TrainCascadeSnapshot(
                    train=before_train,
                    coaches=before_coaches,
                    tickets=before_tickets,
                ),
                after=TrainCascadeSnapshot(
                    train=after_train,
                    coaches=after_coaches,
                    tickets=after_tickets,
                ),
            )
