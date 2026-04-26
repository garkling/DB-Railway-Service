from sqlalchemy import Connection


class BaseRepository:
    def __init__(self, conn: Connection):
        self._conn = conn
