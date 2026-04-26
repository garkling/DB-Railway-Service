from sqlalchemy import bindparam, text

from app.domain.class_facility import ClassFacility
from app.repositories.base import BaseRepository


class ClassFacilityRepository(BaseRepository):
    def list_for_class(self, class_code: str) -> list[ClassFacility]:
        sql = text("""
            SELECT class_code, facility_id
            FROM class_facility
            WHERE class_code = :class_code
            ORDER BY facility_id
        """)
        rows = self._conn.execute(sql, {"class_code": class_code}).mappings().all()
        return [ClassFacility(**r) for r in rows]

    def list_for_class_codes(self, codes: list[str]) -> list[ClassFacility]:
        if not codes:
            return []
        sql = text("""
            SELECT class_code, facility_id
            FROM class_facility
            WHERE class_code IN :codes
            ORDER BY class_code, facility_id
        """).bindparams(bindparam("codes", expanding=True))
        rows = self._conn.execute(sql, {"codes": codes}).mappings().all()
        return [ClassFacility(**r) for r in rows]

    def insert(self, cf: ClassFacility) -> None:
        sql = text("""
            INSERT INTO class_facility (class_code, facility_id)
            VALUES (:class_code, :facility_id)
        """)
        self._conn.execute(sql, cf.__dict__)

    def delete(self, class_code: str, facility_id: int) -> int:
        sql = text("""
            DELETE FROM class_facility
            WHERE class_code = :class_code AND facility_id = :facility_id
        """)
        return self._conn.execute(sql, {
            "class_code": class_code,
            "facility_id": facility_id,
        }).rowcount