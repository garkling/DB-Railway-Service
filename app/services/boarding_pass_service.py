from datetime import date

from sqlalchemy import Engine

from app.domain.reports import BoardingPass
from app.exceptions import TicketNotFound
from app.repositories.operator_repository import OperatorRepository
from app.repositories.passenger_repository import PassengerRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.route_station_repository import RouteStationRepository
from app.repositories.station_repository import StationRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.train_repository import TrainRepository
from app.repositories.travel_class_repository import TravelClassRepository


class BoardingPassService:
    def __init__(self, engine: Engine):
        self._engine = engine

    def build(
        self, train_number: str, service_date: date, ticket_number: int,
    ) -> BoardingPass:
        """Build a single-ticket boarding pass payload (APD-007 §4).

        Composition is in Python (no JOINs across aggregates) per APD-004 §7.
        SQL queries fired in order, all read-only inside engine.connect():

          1. SELECT ... FROM ticket
                 WHERE train_number = :tn AND service_date = :sd AND ticket_number = :n
          2. SELECT ... FROM passenger      WHERE passenger_id = :pid
          3. SELECT ... FROM train          WHERE train_number = :tn AND service_date = :sd
          4. SELECT ... FROM railway_operator WHERE operator_code = :oc
          5. SELECT ... FROM route          WHERE route_id = :rid
          6. SELECT ... FROM travel_class   WHERE class_code = :cc
          7. SELECT ... FROM route_station  WHERE route_id = :rid ORDER BY stop_order
          8. SELECT ... FROM station        WHERE station_code IN :codes

        Raises:
          TicketNotFound: ticket PK does not exist.
        """
        with self._engine.connect() as conn:
            ticket_repo = TicketRepository(conn)
            passenger_repo = PassengerRepository(conn)
            train_repo = TrainRepository(conn)
            operator_repo = OperatorRepository(conn)
            route_repo = RouteRepository(conn)
            class_repo = TravelClassRepository(conn)
            rs_repo = RouteStationRepository(conn)
            station_repo = StationRepository(conn)

            # 1. Ticket (and existence check)
            ticket = ticket_repo.get(train_number, service_date, ticket_number)
            if ticket is None:
                raise TicketNotFound(train_number, service_date, ticket_number)

            # 2-6. FK-target aggregates (FKs guarantee existence)
            passenger = passenger_repo.get(ticket.passenger_id)
            train = train_repo.get(ticket.train_number, ticket.service_date)
            operator = operator_repo.get(train.operator_code)
            route = route_repo.get(train.route_id)
            travel_class = class_repo.get(ticket.class_code)

            # 7. Route stations sorted by stop_order
            stops = rs_repo.list_for_route(train.route_id)

            # 8. Bulk-fetch first + last station (deduped if origin == destination)
            origin_name: str | None = None
            destination_name: str | None = None
            if stops:
                first_code = stops[0].station_code
                last_code = stops[-1].station_code
                stations = station_repo.list_by_codes(
                    list({first_code, last_code}),
                )
                stations_by_code = {s.station_code: s for s in stations}
                first = stations_by_code.get(first_code)
                last = stations_by_code.get(last_code)
                origin_name = first.station_name if first else None
                destination_name = last.station_name if last else None

            return BoardingPass(
                ticket_number=ticket.ticket_number,
                train_number=ticket.train_number,
                service_date=ticket.service_date,
                scheduled_departure=train.scheduled_departure,
                scheduled_arrival=train.scheduled_arrival,
                operator_name=operator.operator_name,
                passenger_full_name=passenger.full_name,
                seat_number=ticket.seat_number,
                class_name=travel_class.class_name,
                class_description=travel_class.description,
                price_paid=ticket.price_paid,
                booking_date=ticket.booking_date,
                origin_station=origin_name,
                destination_station=destination_name,
            )
