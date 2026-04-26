from sqlalchemy import bindparam, text

from app.domain.travel_class import (
    FirstClass,
    SecondClass,
    SleepingClass,
    TravelClass,
)
from app.repositories.base import BaseRepository


class TravelClassRepository(BaseRepository):
    def get(self, class_code: str) -> TravelClass | None:
        sql = text("""
            SELECT class_code, class_name, description, base_price_multiplier
            FROM travel_class
            WHERE class_code = :class_code
        """)
        row = self._conn.execute(sql, {"class_code": class_code}).mappings().first()
        return TravelClass(**row) if row else None

    def exists(self, class_code: str) -> bool:
        sql = text("SELECT 1 FROM travel_class WHERE class_code = :class_code LIMIT 1")
        return self._conn.execute(sql, {"class_code": class_code}).first() is not None

    def list_all(self) -> list[TravelClass]:
        sql = text("""
            SELECT class_code, class_name, description, base_price_multiplier
            FROM travel_class
            ORDER BY class_code
        """)
        return [TravelClass(**r) for r in self._conn.execute(sql).mappings().all()]

    def list_by_codes(self, codes: list[str]) -> list[TravelClass]:
        if not codes:
            return []
        sql = text("""
            SELECT class_code, class_name, description, base_price_multiplier
            FROM travel_class
            WHERE class_code IN :codes
            ORDER BY class_code
        """).bindparams(bindparam("codes", expanding=True))
        rows = self._conn.execute(sql, {"codes": codes}).mappings().all()
        return [TravelClass(**r) for r in rows]

    def insert(self, tc: TravelClass) -> None:
        sql = text("""
            INSERT INTO travel_class (class_code, class_name, description, base_price_multiplier)
            VALUES (:class_code, :class_name, :description, :base_price_multiplier)
        """)
        self._conn.execute(sql, tc.__dict__)

    def update(self, tc: TravelClass) -> int:
        sql = text("""
            UPDATE travel_class
            SET class_name = :class_name,
                description = :description,
                base_price_multiplier = :base_price_multiplier
            WHERE class_code = :class_code
        """)
        return self._conn.execute(sql, tc.__dict__).rowcount

    def delete(self, class_code: str) -> int:
        sql = text("DELETE FROM travel_class WHERE class_code = :class_code")
        return self._conn.execute(sql, {"class_code": class_code}).rowcount

    def get_first_class(self, class_code: str) -> FirstClass | None:
        sql = text("""
            SELECT class_code, lounge_access, complimentary_meal
            FROM first_class
            WHERE class_code = :class_code
        """)
        row = self._conn.execute(sql, {"class_code": class_code}).mappings().first()
        return FirstClass(**row) if row else None

    def insert_first_class(self, fc: FirstClass) -> None:
        sql = text("""
            INSERT INTO first_class (class_code, lounge_access, complimentary_meal)
            VALUES (:class_code, :lounge_access, :complimentary_meal)
        """)
        self._conn.execute(sql, fc.__dict__)

    def update_first_class(self, fc: FirstClass) -> int:
        sql = text("""
            UPDATE first_class
            SET lounge_access = :lounge_access,
                complimentary_meal = :complimentary_meal
            WHERE class_code = :class_code
        """)
        return self._conn.execute(sql, fc.__dict__).rowcount

    def delete_first_class(self, class_code: str) -> int:
        sql = text("DELETE FROM first_class WHERE class_code = :class_code")
        return self._conn.execute(sql, {"class_code": class_code}).rowcount

    def get_second_class(self, class_code: str) -> SecondClass | None:
        sql = text("""
            SELECT class_code, has_folding_table
            FROM second_class
            WHERE class_code = :class_code
        """)
        row = self._conn.execute(sql, {"class_code": class_code}).mappings().first()
        return SecondClass(**row) if row else None

    def insert_second_class(self, sc: SecondClass) -> None:
        sql = text("""
            INSERT INTO second_class (class_code, has_folding_table)
            VALUES (:class_code, :has_folding_table)
        """)
        self._conn.execute(sql, sc.__dict__)

    def update_second_class(self, sc: SecondClass) -> int:
        sql = text("""
            UPDATE second_class
            SET has_folding_table = :has_folding_table
            WHERE class_code = :class_code
        """)
        return self._conn.execute(sql, sc.__dict__).rowcount

    def delete_second_class(self, class_code: str) -> int:
        sql = text("DELETE FROM second_class WHERE class_code = :class_code")
        return self._conn.execute(sql, {"class_code": class_code}).rowcount

    def get_sleeping_class(self, class_code: str) -> SleepingClass | None:
        sql = text("""
            SELECT class_code, berth_type, linens_included, compartment_capacity
            FROM sleeping_class
            WHERE class_code = :class_code
        """)
        row = self._conn.execute(sql, {"class_code": class_code}).mappings().first()
        return SleepingClass(**row) if row else None

    def insert_sleeping_class(self, slp: SleepingClass) -> None:
        sql = text("""
            INSERT INTO sleeping_class (class_code, berth_type, linens_included, compartment_capacity)
            VALUES (:class_code, :berth_type, :linens_included, :compartment_capacity)
        """)
        self._conn.execute(sql, slp.__dict__)

    def update_sleeping_class(self, slp: SleepingClass) -> int:
        sql = text("""
            UPDATE sleeping_class
            SET berth_type = :berth_type,
                linens_included = :linens_included,
                compartment_capacity = :compartment_capacity
            WHERE class_code = :class_code
        """)
        return self._conn.execute(sql, slp.__dict__).rowcount

    def delete_sleeping_class(self, class_code: str) -> int:
        sql = text("DELETE FROM sleeping_class WHERE class_code = :class_code")
        return self._conn.execute(sql, {"class_code": class_code}).rowcount