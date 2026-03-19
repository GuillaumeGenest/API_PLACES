# ─── Récupération IP locale (Mac) ───────────────────────────────
LOCAL_IP := $(shell ipconfig getifaddr en0 || ipconfig getifaddr en1)

update-ip:
	@CURRENT_IP=$$(grep SERVER_BASE_URL_DEV .env | sed 's/.*http:\/\/\(.*\):8000/\1/'); \
	if [ "$$CURRENT_IP" = "$(LOCAL_IP)" ]; then \
		echo "✅ IP inchangée : $(LOCAL_IP)"; \
	else \
		echo ""; \
		echo "⚠️  CHANGEMENT D'IP DÉTECTÉ ⚠️"; \
		echo "Ancienne IP : $$CURRENT_IP"; \
		echo "Nouvelle IP : $(LOCAL_IP)"; \
		echo "Mise à jour du fichier .env"; \
		echo ""; \
		sed -i '' "s|SERVER_BASE_URL_DEV=.*|SERVER_BASE_URL_DEV=http://$(LOCAL_IP):8000|g" .env; \
	fi

# ─── Lancement serveur ───────────────────────────────────────────
dev: update-ip
	ENVIRONMENT=development uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

testing:
	ENVIRONMENT=testing uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

prod:
	ENVIRONMENT=production uvicorn app.main:app --host 0.0.0.0 --port 8000

# ─── Environnement virtuel ───────────────────────────────────────
install:
	python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# ─── Tests ───────────────────────────────────────────────────────
test-unit:
	ENVIRONMENT=testing pytest tests/unit/ -v

# ─── Seeds countries ─────────────────────────────────────────────
country ?=

import-all:
	PYTHONPATH=. python -m scripts.countries_info import_all

import-country:
ifndef country
	$(error ❌ Précise le pays : make import-country country=MA)
endif
	PYTHONPATH=. python -m scripts.countries_info import_one $(country)