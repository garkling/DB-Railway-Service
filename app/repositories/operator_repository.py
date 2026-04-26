from sqlalchemy import bindparam, text

from app.domain.operator import RailwayOperator
from app.repositories.base import BaseRepository


class OperatorRepository(BaseRepository):
    def get(self, operator_code: str) -> RailwayOperator | None:
        sql = text("""
            SELECT operator_code, operator_name, country, contact_phone, base_fare
            FROM railway_operator
            WHERE operator_code = :operator_code
        """)
        row = self._conn.execute(sql, {"operator_code": operator_code}).mappings().first()
        return RailwayOperator(**row) if row else None

    def exists(self, operator_code: str) -> bool:
        sql = text("""
            SELECT 1 FROM railway_operator
            WHERE operator_code = :operator_code
            LIMIT 1
        """)
        return self._conn.execute(sql, {"operator_code": operator_code}).first() is not None

    def list_all(self) -> list[RailwayOperator]:
        sql = text("""
            SELECT operator_code, operator_name, country, contact_phone, base_fare
            FROM railway_operator
            ORDER BY operator_code
        """)
        return [RailwayOperator(**r) for r in self._conn.execute(sql).mappings().all()]

    def list_by_codes(self, codes: list[str]) -> list[RailwayOperator]:
        if not codes:
            return []
        sql = text("""
            SELECT operator_code, operator_name, country, contact_phone, base_fare
            FROM railway_operator
            WHERE operator_code IN :codes
            ORDER BY operator_code
        """).bindparams(bindparam("codes", expanding=True))
        rows = self._conn.execute(sql, {"codes": codes}).mappings().all()
        return [RailwayOperator(**r) for r in rows]

    def insert(self, op: RailwayOperator) -> None:
        sql = text("""
            INSERT INTO railway_operator (operator_code, operator_name, country, contact_phone, base_fare)
            VALUES (:operator_code, :operator_name, :country, :contact_phone, :base_fare)
        """)
        self._conn.execute(sql, op.__dict__)

    def update(self, op: RailwayOperator) -> int:
        sql = text("""
            UPDATE railway_operator
            SET operator_name = :operator_name,
                country = :country,
                contact_phone = :contact_phone,
                base_fare = :base_fare
            WHERE operator_code = :operator_code
        """)
        return self._conn.execute(sql, op.__dict__).rowcount

    def delete(self, operator_code: str) -> int:
        sql = text("""
            DELETE FROM railway_operator
            WHERE operator_code = :operator_code
        """)
        return self._conn.execute(sql, {"operator_code": operator_code}).rowcount