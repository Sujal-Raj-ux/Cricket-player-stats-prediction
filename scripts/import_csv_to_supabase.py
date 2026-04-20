#!/usr/bin/env python3
"""
Load data/ipl_ml_features.csv into Postgres (Supabase).

Usage:
  export DATABASE_URL="postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require"
  python scripts/import_csv_to_supabase.py

Requires: pandas, psycopg2-binary (see requirements.txt)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

# Prefer repo .env over a stale DATABASE_URL exported in the shell.
load_dotenv(ROOT / ".env", override=True)

CSV_PATH = ROOT / "data" / "ipl_ml_features.csv"

INSERT_COLS = [
    "rolling_avg_5",
    "rolling_avg_10",
    "rolling_sr_5",
    "rolling_sr_10",
    "innings_count",
    "career_avg",
    "consistency",
    "bat_pos",
    "innings",
    "is_playoff",
    "toss_bat_first",
    "venue_avg",
    "vs_team_avg",
    "venue_overall_avg",
    "is_home",
    "opp_bowling_econ",
    "opp_bowling_sr",
    "runs",
    "batter",
    "match_id",
    "date",
    "season",
]


def main() -> None:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        print("Set DATABASE_URL to your Supabase Postgres connection string.", file=sys.stderr)
        sys.exit(1)
    if not CSV_PATH.is_file():
        print(f"Missing {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(CSV_PATH, parse_dates=["date"])
    for c in INSERT_COLS:
        if c not in df.columns:
            print(f"CSV missing column: {c}", file=sys.stderr)
            sys.exit(1)

    df = df[INSERT_COLS].copy()
    df = df.where(pd.notna(df), None)

    tuples = [tuple(row) for row in df.itertuples(index=False, name=None)]

    sql = f"""
        INSERT INTO ipl_ml_features ({", ".join(INSERT_COLS)})
        VALUES %s
    """

    try:
        conn = psycopg2.connect(url, connect_timeout=30)
    except psycopg2.OperationalError as e:
        err = str(e).lower()
        print(f"Database connection failed: {e}", file=sys.stderr)
        if "could not translate host name" in err or "nodename nor servname" in err:
            print(
                "\nYour Mac cannot resolve the DB hostname (common with db.*.supabase.co on IPv4-only DNS).\n"
                "Fix: In Supabase → Project Settings → Database, copy the Transaction pooler URI\n"
                "(host like aws-0-REGION.pooler.supabase.com, port 6543, user postgres.PROJECT_REF).\n"
                "Put that in .env as DATABASE_URL and add ?sslmode=require if missing.\n",
                file=sys.stderr,
            )
        elif "ssl" in err or "encryption" in err:
            print("\nTry appending ?sslmode=require to DATABASE_URL.\n", file=sys.stderr)
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ipl_ml_features")
            execute_values(cur, sql, tuples, page_size=2000)
        conn.commit()
        print(f"Inserted {len(tuples)} rows into ipl_ml_features.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
