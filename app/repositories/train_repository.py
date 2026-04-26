from datetime import date

from sqlalchemy import text

from app.domain.train import Train
from app.repositories.base import BaseRepository


class TrainRepository(BaseRepository):
    def get(self, train_number: str, service_date: date) -> Train | None:
        sql = text("""
            SELECT train_number, service_date, scheduled_departure, scheduled_arrival,
                   train_status, operator_code, route_id,
                   actual_departure, actual_arrival, delay_reason, duration_minutes
            FROM train
            WHERE train_number = :train_number AND service_date = :service_date
        """)
        row = self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
        }).mappings().first()
        return Train(**row) if row else None

    def exists(self, train_number: str, service_date: date) -> bool:
        sql = text("""
            SELECT 1 FROM train
            WHERE train_number = :train_number AND service_date = :service_date
            LIMIT 1
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
        }).first() is not None

    def list_all(self) -> list[Train]:
        sql = text("""
            SELECT train_number, service_date, scheduled_departure, scheduled_arrival,
                   train_status, operator_code, route_id,
                   actual_departure, actual_arrival, delay_reason, duration_minutes
            FROM train
            ORDER BY service_date, train_number
        """)
        return [Train(**r) for r in self._conn.execute(sql).mappings().all()]

    def insert(self, train: Train) -> None:
        sql = text("""
            INSERT INTO train (train_number, service_date, scheduled_departure, scheduled_arrival,
                               train_status, operator_code, route_id,
                               actual_departure, actual_arrival, delay_reason)
            VALUES (:train_number, :service_date, :scheduled_departure, :scheduled_arrival,
                    :train_status, :operator_code, :route_id,
                    :actual_departure, :actual_arrival, :delay_reason)
        """)
        self._conn.execute(sql, {
            "train_number": train.train_number,
            "service_date": train.service_date,
            "scheduled_departure": train.scheduled_departure,
            "scheduled_arrival": train.scheduled_arrival,
            "train_status": train.train_status,
            "operator_code": train.operator_code,
            "route_id": train.route_id,
            "actual_departure": train.actual_departure,
            "actual_arrival": train.actual_arrival,
            "delay_reason": train.delay_reason,
        })

    def update(
        self,
        current_train_number: str,
        current_service_date: date,
        new_state: Train,
    ) -> int:
        sql = text("""
            UPDATE train
            SET train_number = :new_train_number,
                service_date = :new_service_date,
                scheduled_departure = :scheduled_departure,
                scheduled_arrival = :scheduled_arrival,
                train_status = :train_status,
                operator_code = :operator_code,
                route_id = :route_id,
                actual_departure = :actual_departure,
                actual_arrival = :actual_arrival,
                delay_reason = :delay_reason
            WHERE train_number = :current_train_number
              AND service_date = :current_service_date
        """)
        return self._conn.execute(sql, {
            "current_train_number": current_train_number,
            "current_service_date": current_service_date,
            "new_train_number": new_state.train_number,
            "new_service_date": new_state.service_date,
            "scheduled_departure": new_state.scheduled_departure,
            "scheduled_arrival": new_state.scheduled_arrival,
            "train_status": new_state.train_status,
            "operator_code": new_state.operator_code,
            "route_id": new_state.route_id,
            "actual_departure": new_state.actual_departure,
            "actual_arrival": new_state.actual_arrival,
            "delay_reason": new_state.delay_reason,
        }).rowcount

    def delete(self, train_number: str, service_date: date) -> int:
        sql = text("""
            DELETE FROM train
            WHERE train_number = :train_number AND service_date = :service_date
        """)
        return self._conn.execute(sql, {
            "train_number": train_number,
            "service_date": service_date,
        }).rowcount