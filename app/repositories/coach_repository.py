from datetime import date

from sqlalchemy import text

from app.domain.coach import (
    Coach,
    DiningCoach,
    LuggageVan,
    SeatingCoach,
    SleepingCoach,
)
from app.repositories.base import BaseRepository


class CoachRepository(BaseRepository):
    def get(self, train_number: str, service_date: date, coach_number: int) -> Coach | None:
        sql = text("""
            SELECT train_number, service_date, coach_number, coach_type,
                   seat_capacity, has_air_conditioning, class_code, owner_operator_code
            FROM coach
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        row = self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).mappings().first()
        return Coach(**row) if row else None

    def exists(self, train_number: str, service_date: date, coach_number: int) -> bool:
        sql = text("""
            SELECT 1 FROM coach
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
            LIMIT 1
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).first() is not None

    def list_for_train(self, train_number: str, service_date: date) -> list[Coach]:
        sql = text("""
            SELECT train_number, service_date, coach_number, coach_type,
                   seat_capacity, has_air_conditioning, class_code, owner_operator_code
            FROM coach
            WHERE train_number = :train_number AND service_date = :service_date
            ORDER BY coach_number
        """)
        rows = self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
        }).mappings().all()
        return [Coach(**r) for r in rows]

    def insert(self, coach: Coach) -> None:
        sql = text("""
            INSERT INTO coach (train_number, service_date, coach_number, coach_type,
                               seat_capacity, has_air_conditioning, class_code, owner_operator_code)
            VALUES (:train_number, :service_date, :coach_number, :coach_type,
                    :seat_capacity, :has_air_conditioning, :class_code, :owner_operator_code)
        """)
        self._conn.execute(sql, coach.__dict__)

    def update(self, coach: Coach) -> int:
        sql = text("""
            UPDATE coach
            SET coach_type = :coach_type,
                seat_capacity = :seat_capacity,
                has_air_conditioning = :has_air_conditioning,
                class_code = :class_code,
                owner_operator_code = :owner_operator_code
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, coach.__dict__).rowcount

    def delete(self, train_number: str, service_date: date, coach_number: int) -> int:
        sql = text("""
            DELETE FROM coach
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).rowcount

    def get_seating_variant(
        self, train_number: str, service_date: date, coach_number: int,
    ) -> SeatingCoach | None:
        sql = text("""
            SELECT train_number, service_date, coach_number, seat_arrangement
            FROM seating_coach
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        row = self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).mappings().first()
        return SeatingCoach(**row) if row else None

    def insert_seating_variant(self, sc: SeatingCoach) -> None:
        sql = text("""
            INSERT INTO seating_coach (train_number, service_date, coach_number, seat_arrangement)
            VALUES (:train_number, :service_date, :coach_number, :seat_arrangement)
        """)
        self._conn.execute(sql, sc.__dict__)

    def update_seating_variant(self, sc: SeatingCoach) -> int:
        sql = text("""
            UPDATE seating_coach
            SET seat_arrangement = :seat_arrangement
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, sc.__dict__).rowcount

    def delete_seating_variant(
        self, train_number: str, service_date: date, coach_number: int,
    ) -> int:
        sql = text("""
            DELETE FROM seating_coach
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).rowcount

    def get_sleeping_variant(
        self, train_number: str, service_date: date, coach_number: int,
    ) -> SleepingCoach | None:
        sql = text("""
            SELECT train_number, service_date, coach_number,
                   number_of_compartments, berths_per_compartment
            FROM sleeping_coach
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        row = self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).mappings().first()
        return SleepingCoach(**row) if row else None

    def insert_sleeping_variant(self, sc: SleepingCoach) -> None:
        sql = text("""
            INSERT INTO sleeping_coach (train_number, service_date, coach_number,
                                        number_of_compartments, berths_per_compartment)
            VALUES (:train_number, :service_date, :coach_number,
                    :number_of_compartments, :berths_per_compartment)
        """)
        self._conn.execute(sql, sc.__dict__)

    def update_sleeping_variant(self, sc: SleepingCoach) -> int:
        sql = text("""
            UPDATE sleeping_coach
            SET number_of_compartments = :number_of_compartments,
                berths_per_compartment = :berths_per_compartment
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, sc.__dict__).rowcount

    def delete_sleeping_variant(
        self, train_number: str, service_date: date, coach_number: int,
    ) -> int:
        sql = text("""
            DELETE FROM sleeping_coach
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).rowcount

    def get_dining_variant(
        self, train_number: str, service_date: date, coach_number: int,
    ) -> DiningCoach | None:
        sql = text("""
            SELECT train_number, service_date, coach_number, number_of_tables, menu_type
            FROM dining_coach
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        row = self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).mappings().first()
        return DiningCoach(**row) if row else None

    def insert_dining_variant(self, dc: DiningCoach) -> None:
        sql = text("""
            INSERT INTO dining_coach (train_number, service_date, coach_number,
                                      number_of_tables, menu_type)
            VALUES (:train_number, :service_date, :coach_number,
                    :number_of_tables, :menu_type)
        """)
        self._conn.execute(sql, dc.__dict__)

    def update_dining_variant(self, dc: DiningCoach) -> int:
        sql = text("""
            UPDATE dining_coach
            SET number_of_tables = :number_of_tables,
                menu_type = :menu_type
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, dc.__dict__).rowcount

    def delete_dining_variant(
        self, train_number: str, service_date: date, coach_number: int,
    ) -> int:
        sql = text("""
            DELETE FROM dining_coach
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).rowcount

    def get_luggage_variant(
        self, train_number: str, service_date: date, coach_number: int,
    ) -> LuggageVan | None:
        sql = text("""
            SELECT train_number, service_date, coach_number, max_weight_kg, has_bicycle_rack
            FROM luggage_van
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        row = self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).mappings().first()
        return LuggageVan(**row) if row else None

    def insert_luggage_variant(self, lv: LuggageVan) -> None:
        sql = text("""
            INSERT INTO luggage_van (train_number, service_date, coach_number,
                                     max_weight_kg, has_bicycle_rack)
            VALUES (:train_number, :service_date, :coach_number,
                    :max_weight_kg, :has_bicycle_rack)
        """)
        self._conn.execute(sql, lv.__dict__)

    def update_luggage_variant(self, lv: LuggageVan) -> int:
        sql = text("""
            UPDATE luggage_van
            SET max_weight_kg = :max_weight_kg,
                has_bicycle_rack = :has_bicycle_rack
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, lv.__dict__).rowcount

    def delete_luggage_variant(
        self, train_number: str, service_date: date, coach_number: int,
    ) -> int:
        sql = text("""
            DELETE FROM luggage_van
            WHERE train_number = :train_number
              AND service_date = :service_date
              AND coach_number = :coach_number
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
            "coach_number": coach_number,
        }).rowcount