"""
Postgres connection pool (Supabase or any DATABASE_URL).
Set DATABASE_URL in the environment, e.g. from Supabase Settings → Database → URI.
Append sslmode=require if your client needs it.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Optional

try:
    from psycopg2 import pool
    from psycopg2.extensions import connection as PGConnection
except ImportError:
    pool = None
    PGConnection = None  # type: ignore[misc, assignment]

_pool: Optional["pool.SimpleConnectionPool"] = None


def is_configured() -> bool:
    return bool(os.environ.get("DATABASE_URL", "").strip())


def _get_pool():
    global _pool
    if pool is None:
        raise RuntimeError("psycopg2 not installed")
    if not is_configured():
        return None
    if _pool is None:
        dsn = os.environ["DATABASE_URL"].strip()
        _pool = pool.SimpleConnectionPool(1, 20, dsn)
    return _pool


@contextmanager
def get_connection() -> Generator[PGConnection, None, None]:
    p = _get_pool()
    if p is None:
        raise RuntimeError("DATABASE_URL not set")
    conn = p.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
