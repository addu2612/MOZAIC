# Local development runbook

## Prereqs

- Docker + Docker Compose v2
- Python 3.11+
- Node 18+

## Backend

```bash
cd backend
cp .env.example .env
python scripts/generate_keys.py   # prints keys; paste into .env

docker compose up -d

# If you run the API locally (recommended for dev):
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head   # requires DATABASE_URL pointing to your running postgres
uvicorn app.main:app --reload

# Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Common issues

- **CORS**: ensure backend allows `http://localhost:5173`.
- **DB migrations**: if using compose-only DB, ensure `DATABASE_URL` points to the correct host.
- **Redis**: Celery requires Redis to be running.
