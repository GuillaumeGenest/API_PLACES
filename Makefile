# ─── Lancement serveur ───────────────────────────────────────────
dev:
	ENVIRONMENT=development uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

testing:
	ENVIRONMENT=testing uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

prod:
	ENVIRONMENT=production uvicorn app.main:app --host 0.0.0.0 --port 8000

# ─── Environnement virtuel ───────────────────────────────────────
install:
	python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

test-unit:
	ENVIRONMENT=testing pytest tests/unit/ -v