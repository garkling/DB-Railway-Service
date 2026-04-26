.DEFAULT_GOAL := help

COMPOSE     ?= docker compose
APP_SERVICE ?= app
DB_SERVICE  ?= db
DB_USER     ?= root
DB_PASS     ?= secret
DB_NAME     ?= railway_service
PYTHON      ?= python

.PHONY: help up down restart build rebuild logs ps shell db-up db-shell migrate reset wipe test run install clean

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start all services in the background
	$(COMPOSE) up -d

down: ## Stop and remove containers
	$(COMPOSE) down

restart: ## Restart the app service
	$(COMPOSE) restart $(APP_SERVICE)

build: ## Build images
	$(COMPOSE) build

rebuild: ## Rebuild images without cache
	$(COMPOSE) build --no-cache

logs: ## Tail logs from the app
	$(COMPOSE) logs -f $(APP_SERVICE)

ps: ## Show running services
	$(COMPOSE) ps

shell: ## Open a bash shell in the app container
	$(COMPOSE) exec $(APP_SERVICE) bash

db-up: ## Start only the database service
	$(COMPOSE) up -d $(DB_SERVICE)

db-shell: ## Open the MySQL client in the db container
	$(COMPOSE) exec $(DB_SERVICE) mysql -u$(DB_USER) -p$(DB_PASS) $(DB_NAME)

migrate: ## Apply any pending migrations (python migrate.py)
	$(PYTHON) migrate.py

reset: ## Drop all tables and re-apply schema + seeds (destructive, keeps the volume)
	$(PYTHON) migrate.py --reset

wipe: ## Tear down docker compose with volumes removed; bring db back up (destructive)
	$(COMPOSE) down -v
	$(COMPOSE) up -d $(DB_SERVICE)

test: ## Run pytest against the configured DATABASE_URL (resets DB at session start)
	$(PYTHON) -m pytest -v

run: ## Run the app locally with reload (no Docker)
	uvicorn app.main:app --reload

install: ## Install dev dependencies into the active Python env
	pip install -e ".[dev]"

clean: ## Remove Python build artifacts and caches
	find . -type d \( -name __pycache__ -o -name '*.egg-info' -o -name .pytest_cache \) -prune -exec rm -rf {} + 2>/dev/null || true
