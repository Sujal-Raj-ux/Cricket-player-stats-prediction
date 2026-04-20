"""
Same contract as ipl_csv: player list and dashboard from Postgres (e.g. Supabase).
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from psycopg2.extras import RealDictCursor

from app.services.db_pool import get_connection
from app.services.features_meta import get_feature_columns, row_features_dict
from app.services.ipl_csv import batter_from_slug, batter_slug, season_for_api


def list_players_from_db(limit: int = 80) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT batter, COUNT(*)::int AS innings_in_sample
                FROM ipl_ml_features
                GROUP BY batter
                ORDER BY innings_in_sample DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
    return [
        {
            "id": batter_slug(str(r["batter"])),
            "name": str(r["batter"]),
            "team": "IPL dataset",
            "innings_in_sample": int(r["innings_in_sample"]),
        }
        for r in rows
    ]


def get_player_summary_db(player_slug: str) -> Optional[dict[str, Any]]:
    try:
        batter = batter_from_slug(player_slug)
    except Exception:
        return None
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT COUNT(*)::int AS n FROM ipl_ml_features WHERE batter = %s",
                (batter,),
            )
            n = cur.fetchone()["n"]
    if n == 0:
        return None
    return {
        "id": player_slug,
        "name": batter,
        "team": "IPL dataset",
        "innings_in_sample": n,
    }


def get_player_dashboard_db(player_slug: str) -> Optional[dict[str, Any]]:
    try:
        batter = batter_from_slug(player_slug)
    except Exception:
        return None

    cols = get_feature_columns()
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM ipl_ml_features
                WHERE batter = %s
                ORDER BY date ASC
                """,
                (batter,),
            )
            rows = cur.fetchall()

    if not rows:
        return None

    innings: list[dict[str, Any]] = []
    for i, r in enumerate(rows, start=1):
        runs = int(r["runs"])
        sr = float(r["rolling_sr_10"]) if r.get("rolling_sr_10") is not None else 120.0
        balls = max(1, int(round(runs * 100 / max(sr, 1))))
        mid = str(r["match_id"])
        out = hash(mid) % 2 == 0
        d = r["date"]
        if isinstance(d, date):
            d_str = d.strftime("%Y-%m-%d")
        else:
            d_str = str(d)[:10]
        innings.append(
            {
                "id": mid,
                "index": i,
                "matchLabel": f"{d_str} · {mid}",
                "runs": runs,
                "ballsFaced": balls,
                "out": out,
                "dismissal": "caught" if out else None,
            }
        )

    last = rows[-1]
    features = row_features_dict(last, cols)
    actual_last = float(last["runs"])
    season = season_for_api(last.get("season"))

    ld = last["date"]
    if isinstance(ld, date):
        ld_str = ld.strftime("%Y-%m-%d")
    else:
        ld_str = str(ld)[:10]

    return {
        "player": {
            "id": player_slug,
            "name": batter,
            "team": "IPL dataset",
        },
        "innings": innings,
        "latest_context": {
            "match_id": str(last["match_id"]),
            "date": ld_str,
            "season": season,
            "actual_runs": actual_last,
        },
        "features_for_prediction": features,
    }
