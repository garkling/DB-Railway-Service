from sqlalchemy import bindparam, text

from app.domain.route import Route
from app.repositories.base import BaseRepository


class RouteRepository(BaseRepository):
    def get(self, route_id: int) -> Route | None:
        sql = text("""
            SELECT route_id, route_name, total_distance_km, distance_price_multiplier
            FROM route
            WHERE route_id = :route_id
        """)
        row = self._conn.execute(sql, {"route_id": route_id}).mappings().first()
        return Route(**row) if row else None

    def exists(self, route_id: int) -> bool:
        sql = text("SELECT 1 FROM route WHERE route_id = :route_id LIMIT 1")
        return self._conn.execute(sql, {"route_id": route_id}).first() is not None

    def list_all(self) -> list[Route]:
        sql = text("""
            SELECT route_id, route_name, total_distance_km, distance_price_multiplier
            FROM route
            ORDER BY route_id
        """)
        return [Route(**r) for r in self._conn.execute(sql).mappings().all()]

    def list_by_ids(self, ids: list[int]) -> list[Route]:
        if not ids:
            return []
        sql = text("""
            SELECT route_id, route_name, total_distance_km, distance_price_multiplier
            FROM route
            WHERE route_id IN :ids
            ORDER BY route_id
        """).bindparams(bindparam("ids", expanding=True))
        rows = self._conn.execute(sql, {"ids": ids}).mappings().all()
        return [Route(**r) for r in rows]

    def insert(self, route: Route) -> int:
        sql = text("""
            INSERT INTO route (route_name, total_distance_km)
            VALUES (:route_name, :total_distance_km)
        """)
        result = self._conn.execute(sql, {
            "route_name": route.route_name,
            "total_distance_km": route.total_distance_km,
        })
        return result.lastrowid

    def update(self, route: Route) -> int:
        sql = text("""
            UPDATE route
            SET route_name = :route_name,
                total_distance_km = :total_distance_km
            WHERE route_id = :route_id
        """)
        return self._conn.execute(sql, {
            "route_id": route.route_id,
            "route_name": route.route_name,
            "total_distance_km": route.total_distance_km,
        }).rowcount

    def delete(self, route_id: int) -> int:
        sql = text("DELETE FROM route WHERE route_id = :route_id")
        return self._conn.execute(sql, {"route_id": route_id}).rowcount