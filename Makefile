# ─── Récupération IP locale (Mac) ───────────────────────────────
LOCAL_IP := $(shell ipconfig getifaddr en0 || ipconfig getifaddr en1)

# ─── Mise à jour IP + Migration URLs Supabase ───────────────────
update-ip:
	@CURRENT_IP=$$(grep SERVER_BASE_URL_DEV .env | sed 's/.*http:\/\/\(.*\):8000/\1/'); \
	if [ "$$CURRENT_IP" = "$(LOCAL_IP)" ]; then \
		echo "✅ IP inchangée : $(LOCAL_IP)"; \
	else \
		echo ""; \
		echo "⚠️  CHANGEMENT D'IP DÉTECTÉ ⚠️"; \
		echo "Ancienne IP : $$CURRENT_IP"; \
		echo "Nouvelle IP : $(LOCAL_IP)"; \
		echo "Mise à jour du fichier .env..."; \
		sed -i '' "s|SERVER_BASE_URL_DEV=.*|SERVER_BASE_URL_DEV=http://$(LOCAL_IP):8000|g" .env; \
		echo "Migration des URLs Supabase..."; \
		ENVIRONMENT=development python3 -c "\
from app.services.supabase_service import update_photo_urls_base_url; \
count = update_photo_urls_base_url('http://$$CURRENT_IP:8000', 'http://$(LOCAL_IP):8000'); \
print(f'✅ {count} attractions mises à jour dans Supabase')"; \
		echo ""; \
	fi

# ─── Environnement virtuel ───────────────────────────────────────
VENV_PATH := .venv
PYTHON := python3
PIP := pip

# ─── ENV ─────────────────────────────────────
# Cible pour installer l'environnement virtuel

install:
	$(PYTHON) -m venv $(VENV_PATH)
	. $(VENV_PATH)/bin/activate && $(PIP) install -r requirements.txt

# Cible pour vérifier et activer l'environnement si nécessaire
ensure-env:
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "ℹ️  Installation de l'environnement virtuel..."; \
		make install; \
	else \
		echo "✅ Environnement virtuel déjà installé."; \
	fi

# Cible pour activer l'environnement virtuel
activate-env:
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "❌ Environnement virtuel non installé. Exécute 'make install' d'abord."; \
		exit 1; \
	fi
	@bash -c "source $(VENV_PATH)/bin/activate"

# Cible pour vérifier et activer l'environnement si nécessaire

check-env: ensure-env
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "ℹ️  Activation de l'environnement virtuel..."; \
		bash -c "source $(VENV_PATH)/bin/activate"; \
	else \
		echo "✅ Environnement déjà activé : $$VIRTUAL_ENV"; \
	fi

# ─── DEV ─────────────────────────────────────
# ─── Lancement serveur ───────────────────────────────────────────
dev: update-ip check-env
	ENVIRONMENT=development uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# ─── TEST ─────────────────────────────────────
testing: check-env
	ENVIRONMENT=testing uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# ─── PROD ─────────────────────────────────────
prod: check-env
	ENVIRONMENT=production uvicorn app.main:app --host 0.0.0.0 --port 8000

# ─── Tests ───────────────────────────────────────────────────────
test-unit: check-env
	ENVIRONMENT=development TESTING=true pytest tests/unit/ -v

test-integration: check-env
	ENVIRONMENT=development pytest tests/integration/ -v

# ─── Tests obligatoire avant de commit ───────────────────────────────────────────────────────
test: check-env
	ENVIRONMENT=development TESTING=true pytest tests/unit/ -v && ENVIRONMENT=development pytest tests/integration/ -v
	
# ─── Tests ciblés ────────────────────────────────────────────────
# Usage : make test-file FILE=tests/unit/test_routes_trips.py
test-file: check-env
	ENVIRONMENT=development TESTING=true pytest $(FILE) -v
	
# Usage : make test-one TEST=tests/unit/test_routes_trips.py::TestCityTrip::test_city_trip_success
test-one: check-env
	ENVIRONMENT=development  TESTING=true pytest $(TEST) -v


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