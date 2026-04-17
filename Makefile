SHELL := /bin/bash

VENV_PATH := .venv
PYTHON := python3

# ─── ENV ─────────────────────────────────────

install:
	$(PYTHON) -m venv $(VENV_PATH)
	. $(VENV_PATH)/bin/activate && pip install -r requirements.txt

ensure-env:
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "ℹ️ install env..."; \
		make install; \
	else \
		echo "✅ env OK"; \
	fi

check-env: ensure-env
	@echo "✅ env ready"

# ─── DEV ─────────────────────────────────────

dev: check-env
	ENVIRONMENT=development uvicorn app.main:app --reload

# ─── TEST ────────────────────────────────────

test:
	ENVIRONMENT=development pytest -v

# ─── IMPORT COUNTRIES ────────────────────────

country ?=
continent ?=

import-all: check-env
	PYTHONPATH=. $(PYTHON) -m scripts.countries_info import_all

import-country: check-env
ifndef country
	$(error ❌ country missing: make import-country country=IE)
endif
	PYTHONPATH=. $(PYTHON) -m scripts.countries_info import_one $(country)

import-continent: check-env
ifndef continent
	$(error ❌ continent missing: make import-continent continent=Europe)
endif
	PYTHONPATH=. $(PYTHON) -m scripts.countries_info import_continent $(continent)