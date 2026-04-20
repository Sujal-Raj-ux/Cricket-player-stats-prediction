from pathlib import Path

from fastapi import APIRouter, HTTPException
from psycopg2 import OperationalError

from app.models.schemas import PredictRequest
from app.services import data_service, ipl_csv, ipl_postgres, model_service
from app.services.db_pool import is_configured

router = APIRouter()

DATA_CSV = Path(__file__).resolve().parents[2] / "data" / "ipl_ml_features.csv"


def _postgres_unavailable(exc: OperationalError) -> HTTPException:
    msg = str(exc).lower()
    if "could not translate host name" in msg or "nodename nor servname" in msg:
        detail = (
            "PostgreSQL host could not be resolved. Use Supabase's Transaction pooler URI "
            "in DATABASE_URL (Project Settings → Database, port 6543, host *.pooler.supabase.com), "
            "not the direct db.*.supabase.co host if your network only resolves IPv4."
        )
    else:
        detail = f"PostgreSQL connection failed: {exc}"
    return HTTPException(status_code=503, detail=detail)


def _dashboard_payload(base: dict) -> dict:
    features = base.pop("features_for_prediction", None)
    payload = {**base, "prediction": None}

    if features and model_service.is_ready():
        try:
            pred = model_service.predict(PredictRequest(features=features))
            payload["prediction"] = pred.model_dump()
        except ValueError as e:
            payload["prediction_error"] = str(e)
        except Exception as e:
            payload["prediction_error"] = f"Prediction failed: {e!s}"
    elif features and not model_service.is_ready():
        payload["prediction_error"] = (
            "Model not loaded (check XGBoost / libomp and ipl_batting_model_v2.pkl)."
        )

    return payload


@router.get("/players")
def list_players():
    if is_configured():
        try:
            return {"players": ipl_postgres.list_players_from_db()}
        except OperationalError as e:
            raise _postgres_unavailable(e) from e
    if DATA_CSV.is_file():
        return {"players": ipl_csv.list_players_from_csv()}
    return {"players": data_service.list_players()}


@router.get("/players/{player_id}")
def get_player(player_id: str):
    if is_configured():
        try:
            summary = ipl_postgres.get_player_summary_db(player_id)
        except OperationalError as e:
            raise _postgres_unavailable(e) from e
        if summary is None:
            raise HTTPException(status_code=404, detail="Player not found")
        return summary
    if DATA_CSV.is_file():
        summary = ipl_csv.get_player_summary(player_id)
        if summary is None:
            raise HTTPException(status_code=404, detail="Player not found")
        return summary
    player = data_service.get_player(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/players/{player_id}/dashboard")
def player_dashboard(player_id: str):
    if is_configured():
        try:
            base = ipl_postgres.get_player_dashboard_db(player_id)
        except OperationalError as e:
            raise _postgres_unavailable(e) from e
        if base is None:
            raise HTTPException(status_code=404, detail="Player not found")
        return _dashboard_payload(base)

    if DATA_CSV.is_file():
        base = ipl_csv.get_player_dashboard(player_id)
        if base is None:
            raise HTTPException(status_code=404, detail="Player not found")
        return _dashboard_payload(base)

    raise HTTPException(
        status_code=503,
        detail="No data source: set DATABASE_URL (Supabase) or add data/ipl_ml_features.csv",
    )
