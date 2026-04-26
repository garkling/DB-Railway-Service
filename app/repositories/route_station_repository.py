from sqlalchemy import bindparam, text

from app.domain.route_station import RouteStation
from app.repositories.base import BaseRepository


class RouteStationRepository(BaseRepository):
    def list_for_route(self, route_id: int) -> list[RouteStation]:
        sql = text("""
            SELECT route_id, station_code, stop_order
            FROM route_station
            WHERE route_id = :route_id
            ORDER BY stop_order
        """)
        rows = self._conn.execute(sql, {"route_id": route_id}).mappings().all()
        return [RouteStation(**r) for r in rows]

    def list_for_route_ids(self, ids: list[int]) -> list[RouteStation]:
        if not ids:
            return []
        sql = text("""
            SELECT route_id, station_code, stop_order
            FROM route_station
            WHERE route_id IN :ids
            ORDER BY route_id, stop_order
        """).bindparams(bindparam("ids", expanding=True))
        rows = self._conn.execute(sql, {"ids": ids}).mappings().all()
        return [RouteStation(**r) for r in rows]

    def insert(self, rs: RouteStation) -> None:
        sql = text("""
            INSERT INTO route_station (route_id, station_code, stop_order)
            VALUES (:route_id, :station_code, :stop_order)
        """)
        self._conn.execute(sql, rs.__dict__)

    def delete(self, route_id: int, station_code: str) -> int:
        sql = text("""
            DELETE FROM route_station
            WHERE route_id = :route_id AND station_code = :station_code
        """)
        return self._conn.execute(sql, {
            "route_id": route_id,
            "station_code": station_code,
        }).rowcount