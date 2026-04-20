from fastapi import APIRouter, HTTPException

from app.models.schemas import PredictRequest, PredictResponse
from app.services import model_service

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict_runs(body: PredictRequest):
    """
    Run the loaded XGBoost model on the provided feature row.
    Placeholder features until your Colab pipeline is wired.
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
