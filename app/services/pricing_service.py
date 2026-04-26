from sqlalchemy import Engine

from app.domain.reports import PricingRow, RoutePricingSchedule
from app.repositories.operator_repository import OperatorRepository
from app.repositories.pricing_repository import PricingRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.travel_class_repository import TravelClassRepository


class RoutePricingService:
    def __init__(self, engine: Engine):
        self._engine = engine

    def build(
        self,
        operator_filter: str | None = None,
        route_filter: int | None = None,
    ) -> RoutePricingSchedule:
        """Build the route pricing schedule.

        Composition is in Python (no JOINs across aggregates).
        SQL queries fired in order, all read-only inside engine.connect():

          1. SELECT ... FROM operator_class_route_pricing
                 WHERE (:op IS NULL OR operator_code = :op)
                   AND (:rid IS NULL OR route_id = :rid)
                 ORDER BY operator_code, class_code, route_id
          2. SELECT ... FROM railway_operator WHERE operator_code IN :codes   (skipped if 0 pricings)
          3. SELECT ... FROM travel_class     WHERE class_code IN :codes      (skipped if 0 pricings)
          4. SELECT ... FROM route            WHERE route_id IN :ids          (skipped if 0 pricings)

        Empty result: returns RoutePricingSchedule with rows=[]. No error.
        """
        with self._engine.connect() as conn:
            pricing_repo = PricingRepository(conn)
            operator_repo = OperatorRepository(conn)
            class_repo = TravelClassRepository(conn)
            route_repo = RouteRepository(conn)

            # 1. Filtered pricings
            pricings = pricing_repo.list_filtered(operator_filter, route_filter)

            # 2-4. Bulk-fetch related entities (skipped if no pricings to enrich)
            operators_by_code: dict[str, object] = {}
            classes_by_code: dict[str, object] = {}
            routes_by_id: dict[int, object] = {}
            if pricings:
                operator_codes = list({p.operator_code for p in pricings})
                class_codes = list({p.class_code for p in pricings})
                route_ids = list({p.route_id for p in pricings})
                operators_by_code = {
                    o.operator_code: o
                    for o in operator_repo.list_by_codes(operator_codes)
                }
                classes_by_code = {
                    c.class_code: c
                    for c in class_repo.list_by_codes(class_codes)
                }
                routes_by_id = {
                    r.route_id: r
                    for r in route_repo.list_by_ids(route_ids)
                }

            rows = [
                PricingRow(
                    operator_code=p.operator_code,
                    operator_name=operators_by_code[p.operator_code].operator_name,
                    class_code=p.class_code,
                    class_name=classes_by_code[p.class_code].class_name,
                    route_id=p.route_id,
                    route_name=routes_by_id[p.route_id].route_name,
                    base_price=p.base_price,
                    total_distance_km=routes_by_id[p.route_id].total_distance_km,
                    distance_price_multiplier=routes_by_id[
                        p.route_id
                    ].distance_price_multiplier,
                )
                for p in pricings
            ]

            rows.sort(key=lambda r: (r.operator_code, r.class_code, r.route_name))

            return RoutePricingSchedule(
                rows=rows,
                operator_filter=operator_filter,
                route_filter=route_filter,
            )
