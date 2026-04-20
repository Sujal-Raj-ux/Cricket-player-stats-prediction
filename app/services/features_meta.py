"""Feature column names from model_metadata_v2.json (shared by CSV and Postgres paths)."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
METADATA_JSON = DATA_DIR / "model_metadata_v2.json"

_FEATURE_COLS: list[str] | None = None


def get_feature_columns() -> list[str]:
    global _FEATURE_COLS
    if _FEATURE_COLS is None:
        with open(METADATA_JSON, encoding="utf-8") as f:
            meta = json.load(f)
        _FEATURE_COLS = [str(x) for x in meta["features"]]
    return _FEATURE_COLS


def _coerce_feature_float(value: Any) -> float:
    """DB/CSV nulls and bad values become 0.0 so model inference does not crash."""
    if value is None:
        return 0.0
    try:
        x = float(value)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if math.isnan(x) else x


def row_features_dict(row: Mapping[str, Any], cols: list[str]) -> dict[str, float]:
    """One model input row from a DB dict or pandas Series-like mapping."""
    get = row.get if hasattr(row, "get") else lambda k: row[k]
    return {c: _coerce_feature_float(get(c)) for c in cols}
