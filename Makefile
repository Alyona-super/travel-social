.PHONY: help migrate-up migrate-down test lint run

help:
	@echo "Available commands:"
	@echo "  make migrate-up    - Apply database migrations"
	@echo "  make migrate-down  - Rollback database migrations"
	@echo "  make test          - Run all tests"
	@echo "  make lint          - Run linters"
	@echo "  make run           - Run all services with docker-compose"

migrate-up:
	docker-compose exec postgres psql -U travel -d travel -f /migrations/up.sql

migrate-down:
	docker-compose exec postgres psql -U travel -d travel -f /migrations/down.sql

test:
	pytest services/*/tests/

lint:
	black --check services/
	flake8 services/

run:
	docker-compose up --build