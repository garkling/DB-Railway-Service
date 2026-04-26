from sqlalchemy import bindparam, text

from app.domain.facility import Facility
from app.repositories.base import BaseRepository


class FacilityRepository(BaseRepository):
    def get(self, facility_id: int) -> Facility | None:
        sql = text("""
            SELECT facility_id, facility_name, facility_description
            FROM facility
            WHERE facility_id = :facility_id
        """)
        row = self._conn.execute(sql, {"facility_id": facility_id}).mappings().first()
        return Facility(**row) if row else None

    def exists(self, facility_id: int) -> bool:
        sql = text("SELECT 1 FROM facility WHERE facility_id = :facility_id LIMIT 1")
        return self._conn.execute(sql, {"facility_id": facility_id}).first() is not None

    def list_all(self) -> list[Facility]:
        sql = text("""
            SELECT facility_id, facility_name, facility_description
            FROM facility
            ORDER BY facility_id
        """)
        return [Facility(**r) for r in self._conn.execute(sql).mappings().all()]

    def list_by_ids(self, ids: list[int]) -> list[Facility]:
        if not ids:
            return []
        sql = text("""
            SELECT facility_id, facility_name, facility_description
            FROM facility
            WHERE facility_id IN :ids
            ORDER BY facility_id
        """).bindparams(bindparam("ids", expanding=True))
        rows = self._conn.execute(sql, {"ids": ids}).mappings().all()
        return [Facility(**r) for r in rows]

    def insert(self, facility: Facility) -> int:
        sql = text("""
            INSERT INTO facility (facility_name, facility_description)
            VALUES (:facility_name, :facility_description)
        """)
        result = self._conn.execute(sql, {
            "facility_name": facility.facility_name,
            "facility_description": facility.facility_description,
        })
        return result.lastrowid

    def update(self, facility: Facility) -> int:
        sql = text("""
            UPDATE facility
            SET facility_name = :facility_name,
                facility_description = :facility_description
            WHERE facility_id = :facility_id
        """)
        return self._conn.execute(sql, {
            "facility_id": facility.facility_id,
            "facility_name": facility.facility_name,
            "facility_description": facility.facility_description,
        }).rowcount

    def delete(self, facility_id: int) -> int:
        sql = text("DELETE FROM facility WHERE facility_id = :facility_id")
        return self._conn.execute(sql, {"facility_id": facility_id}).rowcount