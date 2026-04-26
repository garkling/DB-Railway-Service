from datetime import date

from sqlalchemy import text

from app.domain.ticket import Ticket
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository):
    def get(
        self, train_number: str, service_date: date, ticket_number: int,
    ) -> Ticket | None:
        sql = text("""
            SELECT train_number, service_date, ticket_number, seat_number,
                   price_paid, booking_date, passenger_id, class_code,
                   booking_status, payment_method
            FROM ticket
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND ticket_number = :ticket_number
        """)
        row = self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "ticket_number": ticket_number,
        }).mappings().first()
        return Ticket(**row) if row else None

    def exists(
        self, train_number: str, service_date: date, ticket_number: int,
    ) -> bool:
        sql = text("""
            SELECT 1 FROM ticket
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND ticket_number = :ticket_number
            LIMIT 1
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "ticket_number": ticket_number,
        }).first() is not None

    def list_for_train(self, train_number: str, service_date: date) -> list[Ticket]:
        sql = text("""
            SELECT train_number, service_date, ticket_number, seat_number,
                   price_paid, booking_date, passenger_id, class_code,
                   booking_status, payment_method
            FROM ticket
            WHERE train_number = :train_number AND service_date = :service_date
            ORDER BY ticket_number
        """)
        rows = self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
        }).mappings().all()
        return [Ticket(**r) for r in rows]

    def list_by_passenger(self, passenger_id: str) -> list[Ticket]:
        sql = text("""
            SELECT train_number, service_date, ticket_number, seat_number,
                   price_paid, booking_date, passenger_id, class_code,
                   booking_status, payment_method
            FROM ticket
            WHERE passenger_id = :passenger_id
            ORDER BY service_date, train_number, ticket_number
        """)
        rows = self._conn.execute(sql, {"passenger_id": passenger_id}).mappings().all()
        return [Ticket(**r) for r in rows]

    def next_ticket_number(self, train_number: str, service_date: date) -> int:
        sql = text("""
            SELECT COALESCE(MAX(ticket_number), 0) + 1 AS next_no
            FROM ticket
            WHERE train_number = :train_number AND service_date = :service_date
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
        }).scalar_one()

    def insert(self, ticket: Ticket) -> None:
        sql = text("""
            INSERT INTO ticket (train_number, service_date, ticket_number,
                                seat_number, price_paid, booking_date,
                                passenger_id, class_code,
                                booking_status, payment_method)
            VALUES (:train_number, :service_date, :ticket_number,
                    :seat_number, :price_paid, :booking_date,
                    :passenger_id, :class_code,
                    :booking_status, :payment_method)
        """)
        self._conn.execute(sql, ticket.__dict__)

    def update(self, ticket: Ticket) -> int:
        sql = text("""
            UPDATE ticket
            SET seat_number = :seat_number,
                price_paid = :price_paid,
                booking_date = :booking_date,
                passenger_id = :passenger_id,
                class_code = :class_code,
                booking_status = :booking_status,
                payment_method = :payment_method
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND ticket_number = :ticket_number
        """)
        return self._conn.execute(sql, ticket.__dict__).rowcount

    def delete(
        self, train_number: str, service_date: date, ticket_number: int,
    ) -> int:
        sql = text("""
            DELETE FROM ticket
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND ticket_number = :ticket_number
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "ticket_number": ticket_number,
        }).rowcount