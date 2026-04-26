from decimal import Decimal

from sqlalchemy import text

from app.domain.pricing import OperatorClassRoutePricing
from app.repositories.base import BaseRepository


class PricingRepository(BaseRepository):
    def get(
        self, operator_code: str, class_code: str, route_id: int,
    ) -> OperatorClassRoutePricing | None:
        sql = text("""
            SELECT operator_code, class_code, route_id, base_price
            FROM operator_class_route_pricing
            WHERE operator_code = :operator_code
              AND class_code = :class_code
              AND route_id = :route_id
        """)
        row = self._conn.execute(sql, {
            "operator_code": operator_code,
            "class_code": class_code,
            "route_id": route_id,
        }).mappings().first()
        return OperatorClassRoutePricing(**row) if row else None

    def exists(
        self, operator_code: str, class_code: str, route_id: int,
    ) -> bool:
        sql = text("""
            SELECT 1 FROM operator_class_route_pricing
            WHERE operator_code = :operator_code
              AND class_code = :class_code
              AND route_id = :route_id
            LIMIT 1
        """)
        return self._conn.execute(sql, {
            "operator_code": operator_code,
            "class_code": class_code,
            "route_id": route_id,
        }).first() is not None

    def get_base_price(
        self, operator_code: str, class_code: str, route_id: int,
    ) -> Decimal | None:
        sql = text("""
            SELECT base_price
            FROM operator_class_route_pricing
            WHERE operator_code = :operator_code
              AND class_code = :class_code
              AND route_id = :route_id
        """)
        return self._conn.execute(sql, {
            "operator_code": operator_code,
            "class_code": class_code,
            "route_id": route_id,
        }).scalar()

    def list_filtered(
        self,
        operator_code: str | None = None,
        route_id: int | None = None,
    ) -> list[OperatorClassRoutePricing]:
        # The (:foo IS NULL OR col = :foo) pattern keeps both filter slots optional in
        # one static query. Simpler than bindparam(expanding=True) + dynamic WHERE
        # assembly, and the optimizer eliminates the no-op branch on first execution.
        sql = text("""
            SELECT operator_code, class_code, route_id, base_price
            FROM operator_class_route_pricing
            WHERE (:operator_code IS NULL OR operator_code = :operator_code)
              AND (:route_id IS NULL OR route_id = :route_id)
            ORDER BY operator_code, class_code, route_id
        """)
        rows = self._conn.execute(sql, {
            "operator_code": operator_code,
            "route_id": route_id,
        }).mappings().all()
        return [OperatorClassRoutePricing(**r) for r in rows]

    def insert(self, p: OperatorClassRoutePricing) -> None:
        sql = text("""
            INSERT INTO operator_class_route_pricing (operator_code, class_code, route_id, base_price)
            VALUES (:operator_code, :class_code, :route_id, :base_price)
        """)
        self._conn.execute(sql, p.__dict__)

    def update(self, p: OperatorClassRoutePricing) -> int:
        sql = text("""
            UPDATE operator_class_route_pricing
            SET base_price = :base_price
            WHERE operator_code = :operator_code
              AND class_code = :class_code
              AND route_id = :route_id
        """)
        return self._conn.execute(sql, p.__dict__).rowcount

    def delete(
        self, operator_code: str, class_code: str, route_id: int,
    ) -> int:
        sql = text("""
            DELETE FROM operator_class_route_pricing
            WHERE operator_code = :operator_code
              AND class_code = :class_code
              AND route_id = :route_id
        """)
        return self._conn.execute(sql, {
            "operator_code": operator_code,
            "class_code": class_code,
            "route_id": route_id,
        }).rowcount