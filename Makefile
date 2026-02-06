.PHONY: help backend-venv backend-install backend-dev backend-celery infra-up infra-down frontend-install frontend-dev lint tree

help:
	@echo "MOZAIC clean snapshot"
	@echo
	@echo "Targets:"
	@echo "  infra-up            Start postgres+redis via backend/docker-compose.yml"
	@echo "  infra-down          Stop infrastructure"
	@echo "  backend-venv        Create backend virtualenv"
	@echo "  backend-install     Install backend deps"
	@echo "  backend-dev         Run FastAPI dev server"
	@echo "  backend-celery      Run Celery worker"
	@echo "  frontend-install    Install frontend deps"
	@echo "  frontend-dev        Run Vite dev server"
	@echo "  tree                Show repo tree (depth 3)"

infra-up:
	cd backend && docker compose up -d

infra-down:
	cd backend && docker compose down

backend-venv:
	cd backend && python -m venv .venv

backend-install:
	cd backend && . .venv/bin/activate && pip install -r requirements.txt

backend-dev:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload

backend-celery:
	cd backend && . .venv/bin/activate && celery -A app.workers.celery_app worker --loglevel=info

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

tree:
	@find . -maxdepth 3 -mindepth 1 -print | sed 's|^\./||' | sort
