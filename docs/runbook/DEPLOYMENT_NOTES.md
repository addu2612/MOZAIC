# Deployment notes (starter)

This snapshot does **not** provide a full production deployment.

## Suggested approach

- Containerize backend API + Celery worker(s)
- Use managed Postgres + Redis where possible
- Put a reverse proxy (nginx/Traefik) in front of the API
- Build the frontend and serve as static assets

## Required secrets

- `SECRET_KEY`
- `ENCRYPTION_KEY`
- external provider credentials (AWS keys, Sentry token, etc.)

## Hardening checklist

- TLS everywhere
- Restrict CORS origins
- Use strong, rotated keys
- Add rate limiting + audit logging
- Add observability (metrics, tracing)
