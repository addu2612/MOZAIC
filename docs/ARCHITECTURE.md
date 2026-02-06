# MOZAIC Architecture (high level)

## Components

- **Frontend** (`frontend/`): React + Vite SPA
- **Backend API** (`backend/`): FastAPI (async)
- **DB**: PostgreSQL
- **Background jobs**: Celery worker + Redis broker/backend
- **Ingestion sources**: Kubernetes, Docker, CloudWatch, Grafana, Sentry
- **Orchestration**: `backend/app/mcp/orchestrator.py`
- **Clustering/correlation**: currently simple placeholder logic in backend; additional clustering utilities are in `ml/clustering/`

## Data flow (typical)

1. User authenticates (JWT).
2. User creates a Project.
3. User connects monitoring accounts (credentials stored encrypted via Fernet).
4. Incidents are created by:
   - webhooks (Sentry / CloudWatch), or
   - manual fetch endpoint, or
   - periodic background tasks (optional).
5. Orchestrator fetches signals, clusters/correlates, writes incidents.

## Security notes

- **Never commit** `.env` or credentials.
- Rotate `SECRET_KEY` and `ENCRYPTION_KEY` for any shared environments.
