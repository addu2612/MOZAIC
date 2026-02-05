# Claude Instructions for MOZAIC

## Project Summary
MOZAIC is a FastAPI + React system for multi‑source incident detection and correlation. Backend provides JWT auth, project/account management, webhook ingestion, and incident orchestration. Frontend is a React (Vite) app with protected routes and Axios API client.

## Key Commands
Backend (from backend/):
- Generate keys: python scripts/generate_keys.py
- Start infra: docker-compose up -d
- Migrate: docker-compose exec api alembic upgrade head
- Run API: uvicorn app.main:app --reload
- Run worker: celery -A app.workers.celery_app worker --loglevel=info

Frontend (from New_frontend/):
- npm install
- npm run dev

## Required Environment Variables (Backend)
- DATABASE_URL
- SECRET_KEY
- ENCRYPTION_KEY
- ACCESS_TOKEN_EXPIRE_MINUTES (optional)
- REDIS_URL (optional)
- CELERY_BROKER_URL (optional)
- CELERY_RESULT_BACKEND (optional)

## Main Files
- backend/app/main.py
- backend/app/api/v1/*
- backend/app/mcp/orchestrator.py
- backend/app/workers/*
- New_frontend/src/App.jsx
- New_frontend/src/utils/api.js
- New_frontend/src/pages/*

## Notes
- API base URL in frontend: http://localhost:8000/api/v1
- Webhooks are unauthenticated and routed at /webhooks/*
- Clustering/correlation are placeholders and can be improved
- docker-compose API service is commented out; only DB/Redis/Celery run by default
