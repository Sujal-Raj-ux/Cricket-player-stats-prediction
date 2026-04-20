from fastapi import APIRouter, HTTPException

from app.services import data_service

router = APIRouter()


@router.get("/matchups")
def list_matchups():
    return {"matchups": data_service.list_matchups()}


@router.get("/matchups/{matchup_id}")
def get_matchup(matchup_id: str):
    matchup = data_service.get_matchup(matchup_id)
    if matchup is None:
        raise HTTPException(status_code=404, detail="Matchup not found")
    return matchup
