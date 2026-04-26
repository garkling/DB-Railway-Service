from sqlalchemy import bindparam, text

from app.domain.station import Station
from app.repositories.base import BaseRepository


class StationRepository(BaseRepository):
    def get(self, station_code: str) -> Station | None:
        sql = text("""
            SELECT station_code, station_name, city, country, number_of_platforms
            FROM station
            WHERE station_code = :station_code
        """)
        row = self._conn.execute(sql, {"station_code": station_code}).mappings().first()
        return Station(**row) if row else None

    def exists(self, station_code: str) -> bool:
        sql = text("SELECT 1 FROM station WHERE station_code = :station_code LIMIT 1")
        return self._conn.execute(sql, {"station_code": station_code}).first() is not None

    def list_all(self) -> list[Station]:
        sql = text("""
            SELECT station_code, station_name, city, country, number_of_platforms
            FROM station
            ORDER BY station_code
        """)
        return [Station(**r) for r in self._conn.execute(sql).mappings().all()]

    def list_by_codes(self, codes: list[str]) -> list[Station]:
        if not codes:
            return []
        sql = text("""
            SELECT station_code, station_name, city, country, number_of_platforms
            FROM station
            WHERE station_code IN :codes
            ORDER BY station_code
        """).bindparams(bindparam("codes", expanding=True))
        rows = self._conn.execute(sql, {"codes": codes}).mappings().all()
        return [Station(**r) for r in rows]

    def insert(self, station: Station) -> None:
        sql = text("""
            INSERT INTO station (station_code, station_name, city, country, number_of_platforms)
            VALUES (:station_code, :station_name, :city, :country, :number_of_platforms)
        """)
        self._conn.execute(sql, station.__dict__)

    def update(self, station: Station) -> int:
        sql = text("""
            UPDATE station
            SET station_name = :station_name,
                city = :city,
                country = :country,
                number_of_platforms = :number_of_platforms
            WHERE station_code = :station_code
        """)
        return self._conn.execute(sql, station.__dict__).rowcount

    def delete(self, station_code: str) -> int:
        sql = text("DELETE FROM station WHERE station_code = :station_code")
        return self._conn.execute(sql, {"station_code": station_code}).rowcount