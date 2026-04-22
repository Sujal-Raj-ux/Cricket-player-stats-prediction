from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# One real row shape from ipl_ml_features (feature columns only) — used for OpenAPI /docs example.
# Names must match data/model_metadata_v2.json "features" list.
_EXAMPLE_FEATURES: dict[str, float] = {
    "rolling_avg_5": 11.0,
    "rolling_avg_10": 11.0,
    "rolling_sr_5": 123.15,
    "rolling_sr_10": 123.15,
    "innings_count": 3.0,
    "career_avg": 9.0,
    "consistency": 7.0,
    "bat_pos": 6.0,
    "innings": 2.0,
    "is_playoff": 1.0,
    "toss_bat_first": 0.0,
    "venue_avg": 9.0,
    "vs_team_avg": 9.0,
    "venue_overall_avg": 21.61,
    "is_home": 0.0,
    "opp_bowling_econ": 7.1,
    "opp_bowling_sr": 19.34,
}


class PredictRequest(BaseModel):
    """Request body: one dict of feature name → numeric value, aligned with model training columns."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "features": _EXAMPLE_FEATURES,
            }
        }
    )

    features: dict[str, Any] | None = Field(
        default=None,
        description="Single row of model inputs (same keys as model_metadata_v2.json → features).",
    )


class PredictResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predicted_runs": 24.7,
                "detail": "ok",
                "training_mae": 16.29,
            }
        }
    )

    predicted_runs: float
    detail: str = "ok"
    training_mae: float | None = Field(
        default=None,
        description="MAE from training metadata (e.g. Colab holdout), if available.",
    )
