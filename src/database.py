import os
import sqlite3
from pathlib import Path
from typing import Optional


DEFAULT_DB_NAME = "historian.db"


def _read_schema(schema_path: Optional[Path] = None) -> str:
    if schema_path is None:
        schema_path = Path(__file__).resolve().parent.parent / "schema.sql"
    return schema_path.read_text(encoding="utf-8")


def get_connection(db_path: Optional[Path | str] = None) -> sqlite3.Connection:
    if db_path is None:
        db_path = Path(__file__).resolve().parent.parent / DEFAULT_DB_NAME
    else:
        db_path = Path(db_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(_read_schema())
    conn.commit()
    return conn
