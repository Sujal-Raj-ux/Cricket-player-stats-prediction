"""
Load XGBoost / sklearn artifacts from data/.
Supports Colab export: ipl_batting_model_v2.pkl + model_metadata_v2.json
Legacy: model.json booster, feature_pipeline.joblib, feature_names.json
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

import joblib
import numpy as np
import pandas as pd

from app.models.schemas import PredictRequest, PredictResponse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

_MODEL: Any = None
_FEATURE_PIPELINE: Any = None
_FEATURE_NAMES: list[str] | None = None
_TRAINING_MAE: float | None = None
_USE_XGB_BOOSTER: bool = False


def _paths():
    return {
        "pkl_v2": DATA_DIR / "ipl_batting_model_v2.pkl",
        "metadata_v2": DATA_DIR / "model_metadata_v2.json",
        "model_json": DATA_DIR / "model.json",
        "pipeline": DATA_DIR / "feature_pipeline.joblib",
        "features_json": DATA_DIR / "feature_names.json",
    }


def _load_feature_names_and_mae() -> None:
    global _FEATURE_NAMES, _TRAINING_MAE
    p = _paths()
    if p["metadata_v2"].is_file():
        with open(p["metadata_v2"], encoding="utf-8") as f:
            meta = json.load(f)
        feats = meta.get("features")
        if isinstance(feats, list):
            _FEATURE_NAMES = [str(x) for x in feats]
        mae = meta.get("mae")
        if mae is not None:
            try:
                _TRAINING_MAE = float(mae)
            except (TypeError, ValueError):
                _TRAINING_MAE = None
        return
    if p["features_json"].is_file():
        with open(p["features_json"], encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            _FEATURE_NAMES = [str(x) for x in data]


def load_artifacts() -> None:
    global _MODEL, _FEATURE_PIPELINE, _USE_XGB_BOOSTER
    _load_feature_names_and_mae()
    p = _paths()

    if p["pipeline"].is_file():
        _FEATURE_PIPELINE = joblib.load(p["pipeline"])

    if p["pkl_v2"].is_file():
        try:
            _MODEL = joblib.load(p["pkl_v2"])
            _USE_XGB_BOOSTER = _is_xgb_booster(_MODEL)
            return
        except Exception:
            logger.exception(
                "Failed to load %s (often macOS: run `brew install libomp` for XGBoost).",
                p["pkl_v2"].name,
            )
            _MODEL = None
            _USE_XGB_BOOSTER = False

    if not p["model_json"].is_file():
        return
    try:
        import xgboost as xgb
    except Exception:
        return
    try:
        booster = xgb.Booster()
        booster.load_model(str(p["model_json"]))
        _MODEL = booster
        _USE_XGB_BOOSTER = True
    except Exception:
        _MODEL = None
        _USE_XGB_BOOSTER = False


def _is_xgb_booster(obj: Any) -> bool:
    try:
        from xgboost import Booster

        return isinstance(obj, Booster)
    except Exception:
        return type(obj).__name__ == "Booster"


def is_ready() -> bool:
    return _MODEL is not None


def _features_dataframe(body: PredictRequest) -> pd.DataFrame:
    if body.features:
        row = dict(body.features)
    else:
        row = {k: v for k, v in body.model_dump().items() if k != "features" and v is not None}
    if _FEATURE_NAMES:
        missing = [c for c in _FEATURE_NAMES if c not in row]
        if missing:
            raise ValueError(f"Missing features: {missing}")
        row = {c: row[c] for c in _FEATURE_NAMES}
    return pd.DataFrame([row])


def predict(body: PredictRequest) -> PredictResponse:
    if _MODEL is None:
        raise ValueError("Model not loaded")

    X = _features_dataframe(body)

    if _FEATURE_PIPELINE is not None:
        import xgboost as xgb

        X_t = _FEATURE_PIPELINE.transform(X)
        if hasattr(X_t, "toarray"):
            X_t = X_t.toarray()
        dmatrix = xgb.DMatrix(X_t)
        raw = _MODEL.predict(dmatrix)
    elif _USE_XGB_BOOSTER:
        import xgboost as xgb

        dmatrix = xgb.DMatrix(X)
        raw = _MODEL.predict(dmatrix)
    else:
        raw = _MODEL.predict(X)

    score = float(np.asarray(raw).ravel()[0])
    return PredictResponse(
        predicted_runs=score,
        detail="ok",
        training_mae=_TRAINING_MAE,
    )
