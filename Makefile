# ============================================================
# Makefile — AttritionIQ Platform
# ============================================================
# Usage: make <target>

.PHONY: help install dev build test lint clean docker-up docker-down migrate seed

# Colors
CYAN  = \033[0;36m
GREEN = \033[0;32m
RESET = \033[0m

help: ## Show this help
	@echo ""
	@echo "  $(CYAN)AttritionIQ Platform — Make Targets$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ============================================================
# Development Setup
# ============================================================
install: ## Install all dependencies (backend + frontend + ml)
	@echo "$(CYAN)Installing backend...$(RESET)"
	cd backend && pip install -r requirements.txt
	@echo "$(CYAN)Installing ML service...$(RESET)"
	cd ml_service && pip install -r requirements.txt
	@echo "$(CYAN)Installing frontend...$(RESET)"
	cd frontend && npm install
	@echo "$(GREEN)All dependencies installed!$(RESET)"

env: ## Copy .env.example to .env
	cp .env.example .env
	@echo "$(GREEN).env created — please update values!$(RESET)"

# ============================================================
# Docker Operations
# ============================================================
docker-up: ## Start all Docker services
	docker compose up -d --build
	@echo "$(GREEN)Services starting... Check: http://localhost$(RESET)"

docker-down: ## Stop all Docker services
	docker compose down

docker-logs: ## Follow Docker logs
	docker compose logs -f

docker-reset: ## Full reset (removes volumes)
	docker compose down -v --remove-orphans
	@echo "$(GREEN)All containers and volumes removed$(RESET)"

docker-ps: ## Show running containers
	docker compose ps

# ============================================================
# Database Operations
# ============================================================
migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

migrate-rollback: ## Rollback last migration
	cd backend && alembic downgrade -1

migrate-create: ## Create new migration (usage: make migrate-create MSG="description")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed database with sample data
	cd backend && python -m app.utils.seeder

# ============================================================
# Development Servers
# ============================================================
dev-backend: ## Start FastAPI dev server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-ml: ## Start ML service dev server
	cd ml_service && uvicorn main:app --reload --host 0.0.0.0 --port 8001

dev-frontend: ## Start frontend dev server
	cd frontend && npm run dev

dev-celery: ## Start Celery worker
	cd backend && celery -A app.celery_app worker --loglevel=info

dev-flower: ## Start Celery Flower monitor
	cd backend && celery -A app.celery_app flower --port=5555

# ============================================================
# Testing
# ============================================================
test: ## Run all tests
	@make test-backend
	@make test-ml
	@make test-frontend

test-backend: ## Run backend tests
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

test-ml: ## Run ML service tests
	cd ml_service && pytest tests/ -v

test-frontend: ## Run frontend tests
	cd frontend && npm run test:unit

test-e2e: ## Run Playwright E2E tests
	cd frontend && npx playwright test

test-load: ## Run Locust load tests (headless)
	cd tests/load && locust --headless -u 50 -r 5 -t 60s --host http://localhost:8000

# ============================================================
# Code Quality
# ============================================================
lint: ## Lint all code
	black --check backend/ ml_service/
	isort --check-only backend/ ml_service/
	flake8 backend/ ml_service/ --max-line-length=100
	cd frontend && npm run lint

format: ## Auto-format code
	black backend/ ml_service/
	isort backend/ ml_service/
	cd frontend && npm run format

type-check: ## Run TypeScript type check
	cd frontend && npm run type-check

# ============================================================
# Utilities
# ============================================================
clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name "*.egg-info" -exec rm -rf {} +
	cd frontend && rm -rf dist node_modules/.cache

logs: ## Show application logs (last 100 lines)
	docker compose logs --tail=100

health: ## Check service health
	@curl -s http://localhost:8000/health | python -m json.tool
	@curl -s http://localhost:8001/health | python -m json.tool

# ============================================================
# Production
# ============================================================
build: ## Build production images
	docker compose build --no-cache

push: ## Push images to registry
	docker compose push
