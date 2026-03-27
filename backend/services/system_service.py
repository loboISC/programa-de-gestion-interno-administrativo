from __future__ import annotations

from sqlalchemy import text

from database.connection import session_scope


class SystemService:
    def ping_database(self) -> bool:
        with session_scope() as session:
            session.execute(text("SELECT 1"))
            return True
