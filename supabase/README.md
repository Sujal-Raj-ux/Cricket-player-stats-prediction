# Supabase (Postgres) for IPL features

See the [root README](../README.md) for running the app. This file is only the database setup.

## 1. Create a project

[Supabase](https://supabase.com) → New project → note the **database password**.

## 2. Create the table

**SQL Editor** → paste `migrations/001_ipl_ml_features.sql` → **Run**.

## 3. Connection string

**Project Settings → Database** → use the **Transaction pooler** URI (port **6543**, host `*.pooler.supabase.com`) if the direct `db.*.supabase.co` host does not resolve on your network.

Copy into `.env` at the repo root (add `?sslmode=require` if not already present):

```env
DATABASE_URL=postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require
```

## 4. Load CSV data

From the project root (with venv active):

```bash
pip install -r requirements.txt
export DATABASE_URL="..."   # same as .env
python scripts/import_csv_to_supabase.py
```

## 5. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

`GET /health` should show `"data_backend": "supabase"` when `DATABASE_URL` is set.

## Priority

If `DATABASE_URL` is set, the API reads from **Postgres**. Otherwise it falls back to **`data/ipl_ml_features.csv`**.
