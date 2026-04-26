from sqlalchemy import bindparam, text

from app.domain.passenger import Passenger
from app.repositories.base import BaseRepository


class PassengerRepository(BaseRepository):
    def get(self, passenger_id: str) -> Passenger | None:
        sql = text("""
            SELECT passenger_id, first_name, last_name, date_of_birth, email
            FROM passenger
            WHERE passenger_id = :passenger_id
        """)
        row = self._conn.execute(sql, {"passenger_id": passenger_id}).mappings().first()
        return Passenger(**row) if row else None

    def exists(self, passenger_id: str) -> bool:
        sql = text("SELECT 1 FROM passenger WHERE passenger_id = :passenger_id LIMIT 1")
        return self._conn.execute(sql, {"passenger_id": passenger_id}).first() is not None

    def list_all(self) -> list[Passenger]:
        sql = text("""
            SELECT passenger_id, first_name, last_name, date_of_birth, email
            FROM passenger
            ORDER BY passenger_id
        """)
        return [Passenger(**r) for r in self._conn.execute(sql).mappings().all()]

    def list_by_ids(self, ids: list[str]) -> list[Passenger]:
        if not ids:
            return []
        sql = text("""
            SELECT passenger_id, first_name, last_name, date_of_birth, email
            FROM passenger
            WHERE passenger_id IN :ids
            ORDER BY passenger_id
        """).bindparams(bindparam("ids", expanding=True))
        rows = self._conn.execute(sql, {"ids": ids}).mappings().all()
        return [Passenger(**r) for r in rows]

    def insert(self, p: Passenger) -> None:
        sql = text("""
            INSERT INTO passenger (passenger_id, first_name, last_name, date_of_birth, email)
            VALUES (:passenger_id, :first_name, :last_name, :date_of_birth, :email)
        """)
        self._conn.execute(sql, {
            "passenger_id": p.passenger_id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "date_of_birth": p.date_of_birth,
            "email": p.email,
        })

    def update(self, p: Passenger) -> int:
        sql = text("""
            UPDATE passenger
            SET first_name = :first_name,
                last_name = :last_name,
                date_of_birth = :date_of_birth,
                email = :email
            WHERE passenger_id = :passenger_id
        """)
        return self._conn.execute(sql, {
            "passenger_id": p.passenger_id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "date_of_birth": p.date_of_birth,
            "email": p.email,
        }).rowcount

    def delete(self, passenger_id: str) -> int:
        sql = text("DELETE FROM passenger WHERE passenger_id = :passenger_id")
        return self._conn.execute(sql, {"passenger_id": passenger_id}).rowcount