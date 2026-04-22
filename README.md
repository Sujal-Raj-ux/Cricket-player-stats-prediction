# IPL player outlook

Web dashboard for IPL batting form, innings history, and a simple **next-inning runs outlook**, backed by a **FastAPI** service and your dataset (CSV or **Postgres** via Supabase).

## Stack

| Layer | Tech |
|--------|------|
| API | Python 3.10+, FastAPI, Uvicorn |
| ML | XGBoost (model artifacts in `data/`) |
| Data | `data/ipl_ml_features.csv` and/or Postgres (`ipl_ml_features`) |
| UI | Vite, React, Tailwind CSS v4, Recharts |

## Prerequisites

- **Python 3.10+** and a virtual environment  
- **Node.js 18+** and npm (for the frontend)  
- **macOS only (optional):** if the model fails to load, install OpenMP: `brew install libomp`

## Quick start

### 1. Clone and Python env

```bash
git clone <your-repo-url>
cd Cricket-player-stats-prediction
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
```

Edit **`.env`** at the repo root:

- **`DATABASE_URL`** — Optional. Postgres URI (e.g. Supabase **transaction pooler**, port `6543`, `?sslmode=require`). If unset, the API uses **`data/ipl_ml_features.csv`** when that file exists.
- **`CORS_ORIGINS`** — Optional. Comma-separated frontend URLs for production (e.g. `https://yourapp.example.com`).

Never commit **`.env`** (it is gitignored).

### 3. Run the API

From the **repository root**:

```bash
uvicorn app.main:app --reload --port 8000
```

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- OpenAPI docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) (`data_backend`: `supabase`, `csv`, or `stub`; `model_ready` reflects the loaded model)

### 4. Run the frontend

```bash
cd web
cp .env.example .env
# Optional: set VITE_API_URL if the API is not at http://127.0.0.1:8000
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

Build for production:

```bash
npm run build
npm run preview   # optional local preview of dist/
```

## Database (Supabase / Postgres)

Full steps: **[`supabase/README.md`](supabase/README.md)** (migrations, pooler URI, loading CSV with `scripts/import_csv_to_supabase.py`).

If you already applied an older schema, run `supabase/migrations/002_season_text.sql` if needed so the `season` column matches string values like `2009/10`.

## Docker (API only)

```bash
docker build -t ipl-api .
docker run --rm -p 8000:8000 --env-file .env ipl-api
```

The image copies **`app/`** and **`data/`** (including model files). Set **`CORS_ORIGINS`** for your deployed frontend.

## Project layout

```
app/           # FastAPI app (routers, services)
data/          # Model + CSVs (tracked; keep secrets out of commits)
web/           # Vite + React UI
scripts/       # e.g. import CSV into Postgres
supabase/      # SQL migrations + Supabase notes
```

## License

Add a `LICENSE` file if you want an explicit open-source license.
