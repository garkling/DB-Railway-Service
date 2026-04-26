from datetime import date

from sqlalchemy import Engine

from app.domain.reports import ManifestRow, TrainManifest
from app.exceptions import TrainNotFound
from app.repositories.operator_repository import OperatorRepository
from app.repositories.passenger_repository import PassengerRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.train_repository import TrainRepository
from app.repositories.travel_class_repository import TravelClassRepository


class TrainManifestService:
    def __init__(self, engine: Engine):
        self._engine = engine

    def build(self, train_number: str, service_date: date) -> TrainManifest:
        """Build a train manifest payload (APD-007 §5).

        Composition is in Python (no JOINs across aggregates) per APD-004 §7.2.
        SQL queries fired in order, all read-only inside engine.connect():

          1. SELECT ... FROM train         WHERE train_number = :tn AND service_date = :sd
          2. SELECT ... FROM railway_operator WHERE operator_code = :oc
          3. SELECT ... FROM route         WHERE route_id = :rid
          4. SELECT ... FROM ticket        WHERE train_number = :tn AND service_date = :sd
                                           ORDER BY ticket_number
          5. SELECT ... FROM passenger     WHERE passenger_id IN :pids   (only if tickets exist)
          6. SELECT ... FROM travel_class  WHERE class_code IN :ccs      (only if tickets exist)

        Empty manifest (train with zero tickets) returns total_passengers=0, rows=[]
        and skips queries 5 and 6.

        Raises:
          TrainNotFound: train PK does not exist.
        """
        with self._engine.connect() as conn:
            train_repo = TrainRepository(conn)
            operator_repo = OperatorRepository(conn)
            route_repo = RouteRepository(conn)
            ticket_repo = TicketRepository(conn)
            passenger_repo = PassengerRepository(conn)
            class_repo = TravelClassRepository(conn)

            # 1. Train existence check
            train = train_repo.get(train_number, service_date)
            if train is None:
                raise TrainNotFound(train_number, service_date)

            # 2-3. FK targets
            operator = operator_repo.get(train.operator_code)
            route = route_repo.get(train.route_id)

            # 4. Tickets, sorted by ticket_number (ORDER BY in repo)
            tickets = ticket_repo.list_for_train(train_number, service_date)

            # 5-6. Bulk-fetch related passengers and classes (skipped if no tickets)
            passengers_by_id: dict[str, object] = {}
            classes_by_code: dict[str, object] = {}
            if tickets:
                passenger_ids = list({t.passenger_id for t in tickets})
                class_codes = list({t.class_code for t in tickets})
                passengers_by_id = {
                    p.passenger_id: p
                    for p in passenger_repo.list_by_ids(passenger_ids)
                }
                classes_by_code = {
                    c.class_code: c
                    for c in class_repo.list_by_codes(class_codes)
                }

            rows = [
                ManifestRow(
                    ticket_number=t.ticket_number,
                    seat_number=t.seat_number,
                    passenger_id=t.passenger_id,
                    passenger_full_name=passengers_by_id[t.passenger_id].full_name,
                    class_code=t.class_code,
                    class_name=classes_by_code[t.class_code].class_name,
                    price_paid=t.price_paid,
                    booking_date=t.booking_date,
                )
                for t in sorted(tickets, key=lambda x: x.ticket_number)
            ]

            return TrainManifest(
                train_number=train.train_number,
                service_date=train.service_date,
                scheduled_departure=train.scheduled_departure,
                scheduled_arrival=train.scheduled_arrival,
                operator_code=operator.operator_code,
                operator_name=operator.operator_name,
                route_id=route.route_id,
                route_name=route.route_name,
                total_passengers=len(rows),
                rows=rows,
            )
