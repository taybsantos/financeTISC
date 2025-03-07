.PHONY: install run test lint format migrate init-db help

# Variables
PYTHON = python3
VENV = venv
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
ALEMBIC = $(VENV)/bin/alembic
BLACK = $(VENV)/bin/black
FLAKE8 = $(VENV)/bin/flake8
ISORT = $(VENV)/bin/isort

help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  run        - Run the application"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linters"
	@echo "  format     - Format code"
	@echo "  migrate    - Run database migrations"
	@echo "  init-db    - Initialize database with default data"

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

run:
	$(PYTHON) run.py

test:
	$(PYTEST) -v --cov=backend tests/

lint:
	$(FLAKE8) backend tests
	$(BLACK) --check backend tests
	$(ISORT) --check-only backend tests

format:
	$(BLACK) backend tests
	$(ISORT) backend tests

migrate:
	$(ALEMBIC) upgrade head

init-db:
	$(PYTHON) scripts/init_db.py

# Development setup
setup: install migrate init-db
	@echo "Development environment setup complete"

# Clean up
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
