# MOZAIC Backend

Multi-Source Orchestrated Zephyr Anomaly Intelligent Coordinator

## Setup

1. Generate encryption keys:
```bash
python scripts/generate_keys.py
```

2. Create `.env` file from `.env.example` and add generated keys

3. Start services:
```bash
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec api alembic upgrade head
```

## API Endpoints

### Auth
- POST `/api/v1/auth/register` - Register user
- POST `/api/v1/auth/login` - Login

### Projects
- POST `/api/v1/projects/` - Create project
- GET `/api/v1/projects/` - List projects
- GET `/api/v1/projects/{id}` - Get project
- PUT `/api/v1/projects/{id}` - Update project
- DELETE `/api/v1/projects/{id}` - Delete project

### Accounts
- POST `/api/v1/accounts/` - Connect account
- GET `/api/v1/accounts/project/{id}` - List project accounts
- DELETE `/api/v1/accounts/{id}` - Delete account

### Incidents
- GET `/api/v1/incidents/project/{id}` - List project incidents
- GET `/api/v1/incidents/{id}` - Get incident details

### Webhooks
- POST `/webhooks/sentry/{project_id}` - Sentry webhook
- POST `/webhooks/cloudwatch/{project_id}` - CloudWatch SNS webhook

## Development
```bash
uvicorn app.main:app --reload
celery -A app.workers.celery_app worker --loglevel=info
```