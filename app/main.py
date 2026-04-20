import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import matchups, players, predict
from app.services import model_service
from app.services.db_pool import close_pool, is_configured

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

_DEFAULT_CORS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def _cors_allow_origins() -> list[str]:
    extra = os.environ.get("CORS_ORIGINS", "").strip()
    if not extra:
        return list(_DEFAULT_CORS)
    merged = list(_DEFAULT_CORS)
    for part in extra.split(","):
        o = part.strip()
        if o and o not in merged:
            merged.append(o)
    return merged


@asynccontextmanager
async def lifespan(_: FastAPI):
    model_service.load_artifacts()
    yield
    close_pool()


app = FastAPI(
    title="IPL Player Stats API",
    description="Prediction and player data for the dashboard.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/api", tags=["predict"])
app.include_router(players.router, prefix="/api", tags=["players"])
app.include_router(matchups.router, prefix="/api", tags=["matchups"])


@app.get("/health")
def health():
    csv_ok = (PROJECT_ROOT / "data" / "ipl_ml_features.csv").is_file()
    backend = "supabase" if is_configured() else ("csv" if csv_ok else "stub")
    return {
        "status": "ok",
        "data_dir": str(PROJECT_ROOT / "data"),
        "data_backend": backend,
        "model_ready": model_service.is_ready(),
    }
