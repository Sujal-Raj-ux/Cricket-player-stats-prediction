from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """
    Either pass a generic features dict (recommended) or add explicit fields
    to match your Colab schema.
    """

    features: dict[str, Any] | None = Field(
        default=None,
        description="Single-row features as name -> value, matching training columns.",
    )


class PredictResponse(BaseModel):
    predicted_runs: float
    detail: str = "ok"
    training_mae: float | None = Field(
        default=None,
        description="MAE from training metadata (e.g. Colab holdout), if available.",
    )
