from datetime import date

from sqlalchemy import Engine

from app.domain.reports import CancelTicketResult
from app.domain.ticket import Ticket
from app.exceptions import (
    PassengerNotFound,
    PricingNotConfigured,
    TicketNotFound,
    TrainNotFound,
    TravelClassNotFound,
)
from app.repositories.passenger_repository import PassengerRepository
from app.repositories.pricing_repository import PricingRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.train_repository import TrainRepository
from app.repositories.travel_class_repository import TravelClassRepository
from app.services.commands import CancelTicketCommand, IssueTicketCommand


class TicketService:
    def __init__(self, engine: Engine):
        self._engine = engine

    def issue_ticket(self, cmd: IssueTicketCommand) -> Ticket:
        """Issue a new ticket; orchestrates the 6 SQL queries.

        1. SELECT 1 FROM passenger WHERE passenger_id = :passenger_id LIMIT 1
        2. SELECT ... FROM train WHERE train_number = :tn AND service_date = :sd
        3. SELECT 1 FROM travel_class WHERE class_code = :class_code LIMIT 1
        4. SELECT base_price FROM operator_class_route_pricing WHERE ...
        5. SELECT COALESCE(MAX(ticket_number), 0) + 1 FROM ticket WHERE ...
        6. INSERT INTO ticket (...) VALUES (...)
        """
        with self._engine.begin() as conn:
            passenger_repo = PassengerRepository(conn)
            train_repo = TrainRepository(conn)
            class_repo = TravelClassRepository(conn)
            pricing_repo = PricingRepository(conn)
            ticket_repo = TicketRepository(conn)

            if not passenger_repo.exists(cmd.passenger_id):
                raise PassengerNotFound(cmd.passenger_id)

            train = train_repo.get(cmd.train_number, cmd.service_date)
            if train is None:
                raise TrainNotFound(cmd.train_number, cmd.service_date)

            if not class_repo.exists(cmd.class_code):
                raise TravelClassNotFound(cmd.class_code)

            base_price = pricing_repo.get_base_price(
                train.operator_code, cmd.class_code, train.route_id,
            )
            if base_price is None:
                raise PricingNotConfigured(
                    train.operator_code, cmd.class_code, train.route_id,
                )

            ticket_number = ticket_repo.next_ticket_number(
                cmd.train_number, cmd.service_date,
            )

            new_ticket = Ticket(
                train_number=cmd.train_number,
                service_date=cmd.service_date,
                ticket_number=ticket_number,
                seat_number=cmd.seat_number,
                price_paid=base_price,
                booking_date=cmd.booking_date,
                passenger_id=cmd.passenger_id,
                class_code=cmd.class_code,
                booking_status="confirmed",
                payment_method="card",
            )
            ticket_repo.insert(new_ticket)
            return new_ticket

    def list_tickets_for_train(
        self, train_number: str, service_date: date,
    ) -> list[Ticket]:
        with self._engine.connect() as conn:
            return TicketRepository(conn).list_for_train(train_number, service_date)

    def cancel_ticket(self, cmd: CancelTicketCommand) -> CancelTicketResult:
        """Delete a ticket;

        SQL queries fired in order inside engine.begin():
          1. SELECT ... FROM ticket WHERE PK              -- captures the ticket data
          2. SELECT ... FROM ticket WHERE (train, date)   -- before snapshot
          3. DELETE FROM ticket WHERE PK
          4. SELECT ... FROM ticket WHERE (train, date)   -- after snapshot
        """
        with self._engine.begin() as conn:
            ticket_repo = TicketRepository(conn)

            captured = ticket_repo.get(
                cmd.train_number, cmd.service_date, cmd.ticket_number,
            )
            if captured is None:
                raise TicketNotFound(
                    cmd.train_number, cmd.service_date, cmd.ticket_number,
                )

            before = ticket_repo.list_for_train(cmd.train_number, cmd.service_date)
            ticket_repo.delete(
                cmd.train_number, cmd.service_date, cmd.ticket_number,
            )
            after = ticket_repo.list_for_train(cmd.train_number, cmd.service_date)

            return CancelTicketResult(
                deleted_ticket=captured,
                before_tickets=before,
                after_tickets=after,
            )
