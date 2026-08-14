"""Engine and session factory, with the SQLite pragmas this schema depends on."""

import sqlite3
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

BUSY_TIMEOUT_MS = 5000


@event.listens_for(Engine, "connect")
def _set_sqlite_pragmas(dpapi_connection: Any, connection_record: Any) -> None:
    """Apply the required pragmas to every new SQLite connection."""
    if not isinstance(dpapi_connection, sqlite3.Connection):
        return

    cursor = dpapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
    cursor.close()


def create_db_engine(url: str) -> Engine:
    """Create an engine for `url`. Pragmas are applied by the connect listener."""
    return create_engine(url)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build a session factory bound to `engine`."""
    return sessionmaker(bind=engine)
