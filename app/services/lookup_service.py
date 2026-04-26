from datetime import date

from sqlalchemy import Engine

from app.domain.operator import RailwayOperator
from app.domain.passenger import Passenger
from app.domain.route import Route
from app.domain.ticket import Ticket
from app.domain.train import Train
from app.domain.travel_class import TravelClass
from app.repositories.operator_repository import OperatorRepository
from app.repositories.passenger_repository import PassengerRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.train_repository import TrainRepository
from app.repositories.travel_class_repository import TravelClassRepository


class LookupService:
    def __init__(self, engine: Engine):
        self._engine = engine

    def trains_for_dropdown(self) -> list[Train]:
        with self._engine.connect() as conn:
            return TrainRepository(conn).list_all()

    def trains_with_tickets_for_dropdown(self) -> list[Train]:
        with self._engine.connect() as conn:
            train_repo = TrainRepository(conn)
            ticket_repo = TicketRepository(conn)
            trains = train_repo.list_all()
            return [
                t for t in trains
                if ticket_repo.list_for_train(t.train_number, t.service_date)
            ]

    def passengers_for_dropdown(self) -> list[Passenger]:
        with self._engine.connect() as conn:
            return PassengerRepository(conn).list_all()

    def travel_classes(self) -> list[TravelClass]:
        with self._engine.connect() as conn:
            return TravelClassRepository(conn).list_all()

    def tickets_for_train(
        self, train_number: str, service_date: date,
    ) -> list[Ticket]:
        with self._engine.connect() as conn:
            return TicketRepository(conn).list_for_train(train_number, service_date)

    def operators_for_dropdown(self) -> list[RailwayOperator]:
        with self._engine.connect() as conn:
            return OperatorRepository(conn).list_all()

    def routes_for_dropdown(self) -> list[Route]:
        with self._engine.connect() as conn:
            return RouteRepository(conn).list_all()
