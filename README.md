# MOZAIC (clean snapshot)

This folder is a **clean, reproducible repo snapshot** of the MOZAIC project.

## Proposed repo structure

```
mozaic-clean/
  backend/        # FastAPI + SQLAlchemy + Alembic + Celery
  frontend/       # React + Vite UI
  ml/             # ML + clustering utilities (no training run in this snapshot)
  research/       # notebooks/experiments (kept lightweight; add as needed)
  docs/           # runbooks + architecture + ADRs
  paper/          # IEEEtran LaTeX paper skeleton
  scripts/        # helper scripts (dev, lint, etc.)
```

## Quickstart (local dev)

### 1) Backend

```bash
cd backend
cp .env.example .env
# edit .env (set SECRET_KEY and ENCRYPTION_KEY at minimum)
docker compose up -d
# optional: run migrations inside the container if api service is enabled
# docker compose exec api alembic upgrade head

# run API locally (if not using the compose api service)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# celery (requires redis)
celery -A app.workers.celery_app worker --loglevel=info
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend currently calls the API at `http://localhost:8000/api/v1` (see `frontend/src/utils/api.js`).

## Documentation

- `docs/runbook/LOCAL_DEV.md`
- `docs/runbook/DEPLOYMENT_NOTES.md`
- `docs/ARCHITECTURE.md`

## Paper

See `paper/` for an IEEEtran skeleton.

## Notes

- This snapshot intentionally excludes secrets (`.env`, private keys) and generated artifacts (`node_modules/`, `dist/`, ML outputs).
- No training or result generation is performed in this snapshot.
