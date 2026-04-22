from fastapi import APIRouter, HTTPException

from app.models.schemas import PredictRequest, PredictResponse
from app.services import model_service

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict_runs(body: PredictRequest):
    """
    Run the loaded model on a single feature row. Keys in `features` must match
    `data/model_metadata_v2.json` (see OpenAPI **Example Value** for a full sample).
    """
    if not model_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Add model + pipeline files under data/ and restart.",
        )
    try:
        return model_service.predict(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
