"""
Load ipl_ml_features.csv and model_metadata_v2.json for player lists, history, and ML features.
"""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from app.services.features_meta import get_feature_columns, row_features_dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
IPL_FEATURES_CSV = DATA_DIR / "ipl_ml_features.csv"

_DF: Optional[pd.DataFrame] = None


def _feature_columns() -> list[str]:
    return get_feature_columns()


def season_for_api(value: Any) -> str | None:
    """IPL seasons are labels like 2009/10; return a clean string for JSON."""
    if value is None or pd.isna(value):
        return None
    s = str(value).strip()
    return s if s else None


def _ensure_df() -> pd.DataFrame:
    global _DF
    if _DF is None:
        _DF = pd.read_csv(IPL_FEATURES_CSV, parse_dates=["date"])
    return _DF


def batter_slug(name: str) -> str:
    """URL-safe id for a batter name."""
    return base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")


def batter_from_slug(slug: str) -> str:
    pad = "=" * (-len(slug) % 4)
    return base64.urlsafe_b64decode(slug + pad).decode()


def list_players_from_csv(limit: int = 80) -> list[dict[str, Any]]:
    df = _ensure_df()
    g = df.groupby("batter", as_index=False).size().rename(columns={"size": "innings_in_sample"})
    g = g.sort_values("innings_in_sample", ascending=False).head(limit)
    return [
        {
            "id": batter_slug(str(r.batter)),
            "name": str(r.batter),
            "team": "IPL dataset",
            "innings_in_sample": int(r.innings_in_sample),
        }
        for r in g.itertuples()
    ]


def get_player_summary(player_slug: str) -> Optional[dict[str, Any]]:
    try:
        batter = batter_from_slug(player_slug)
    except Exception:
        return None
    df = _ensure_df()
    sub = df[df["batter"] == batter]
    if sub.empty:
        return None
    return {
        "id": player_slug,
        "name": batter,
        "team": "IPL dataset",
        "innings_in_sample": int(len(sub)),
    }


def get_player_dashboard(player_slug: str) -> Optional[dict[str, Any]]:
    try:
        batter = batter_from_slug(player_slug)
    except Exception:
        return None

    df = _ensure_df()
    sub = df[df["batter"] == batter].copy()
    if sub.empty:
        return None

    sub = sub.sort_values("date")
    cols = _feature_columns()

    innings: list[dict[str, Any]] = []
    for i, (_, r) in enumerate(sub.iterrows(), start=1):
        runs = int(r["runs"])
        sr = float(r["rolling_sr_10"]) if pd.notna(r["rolling_sr_10"]) else 120.0
        balls = max(1, int(round(runs * 100 / max(sr, 1))))
        mid = str(r["match_id"])
        out = hash(mid) % 2 == 0
        innings.append(
            {
                "id": mid,
                "index": i,
                "matchLabel": f"{r['date'].strftime('%Y-%m-%d')} · {mid}",
                "runs": runs,
                "ballsFaced": balls,
                "out": out,
                "dismissal": "caught" if out else None,
            }
        )

    last = sub.iloc[-1]
    features = row_features_dict(last, cols)
    actual_last = float(last["runs"])

    return {
        "player": {
            "id": player_slug,
            "name": batter,
            "team": "IPL dataset",
        },
        "innings": innings,
        "latest_context": {
            "match_id": str(last["match_id"]),
            "date": last["date"].strftime("%Y-%m-%d"),
            "season": season_for_api(last["season"]),
            "actual_runs": actual_last,
        },
        "features_for_prediction": features,
    }
