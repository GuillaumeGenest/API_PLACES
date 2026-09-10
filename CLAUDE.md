# Règles projet — Places API (CLAUDE.md)

## Local Overrides

- Si `CLAUDE.local.md` existe à la racine (fichier personnel, non committé), le lire d'abord.
- Ses instructions priment sur celles de ce document en cas de conflit — notamment tout le workflow git/build/test.

## Overview

- **Project Name**: Places API
- **Description**: API FastAPI qui fournit des informations sur des attractions touristiques (lieux touristiques, nature, restaurants, autres) via l'API Google Places, avec recherche par ville, coordonnées, ou nom/adresse.
- **Repository**: [GuillaumeGenest/API_PLACES](git@github.com:GuillaumeGenest/API_PLACES.git)
- **Scope**: Backend consommé par les apps SunnyOnRoads iOS et Android (recherche de lieux, autocomplete, trips, IA, cache d'images, infos pays)
- **Documentation**: `README.md` (routes disponibles), `commandes.md` (commandes courantes, variables SESSION, exemples curl)

## Tech Stack

- **Langage**: Python (FastAPI, Pydantic v2)
- **Serveur**: Uvicorn
- **Base de données**: Supabase (Postgres via `supabase`/`postgrest`/`storage3`), SQLAlchemy
- **Auth**: Supabase Auth (JWT)
- **IA**: OpenAI (génération de trips/descriptions)
- **Gestionnaire d'environnement**: `venv` (via `make install`)
- **Tests**: pytest
- **Conteneurisation**: Docker (`Dockerfile`)
- **CI/CD**: GitHub Actions (`.github/workflows/`)

## Project Structure

- **`app/api/`** — clients bas niveau vers les API externes (Google Places Autocomplete, Photos, Places, Places AI, Trip)
- **`app/core/`** — config, DB, sécurité, logger, exceptions, init DB
- **`app/models/`** — modèles Pydantic (`attraction`, `common`, `country_info`, `trip`)
- **`app/routers/`** — endpoints FastAPI (`attraction`, `attractions`, `search`, `trips`, `images`, `countries_info`, `descriptions`, `ai`, `users`)
- **`app/services/`** — logique métier (places, photos, autocomplete, storage, supabase, country_info, trip, ai)
- **`app/main.py`** — point d'entrée FastAPI
- **`tests/unit/`** — tests unitaires par route (`test_routes_*.py`)
- **`tests/integration/`** — tests d'intégration (ex: `test_auth.py`)
- **`scripts/`** — scripts d'automatisation (ex: import pays)
- **`seeds/`** — données de seed

## Development Rules

### Language

- Code, commentaires et messages de commit : toujours en anglais (cohérent avec l'historique existant, ex. `[SOR-xxx] ...`).
- Réponses dans la conversation : en français, comme établi dans nos échanges.

### Workflow

Voir `CLAUDE.local.md` — c'est la référence pour tout ce qui touche git, commits, PR, builds et tests sur ce repo.

### AI-Assisted Development

1. **Plan First** — pour toute tâche d'implémentation (hors fix trivial mono-fichier ou question informative), présenter le plan et attendre validation avant de commencer.
2. **Self-Improvement** — après une correction, retenir le pattern pour ne pas répéter l'erreur (mémoire du projet).
3. **Code Quality Check** — pour un changement non trivial : vérifier que l'approche suit les conventions du projet, minimise la complexité, réutilise les patterns/abstractions existants (services/routers/models déjà en place). Reconsidérer si une solution semble bancale.
4. **Review and reasoning from code** — pour le comportement, l'intention, les cas limites et la correction, se baser uniquement sur le **code exécutable et les tests**. Ne pas utiliser les commentaires inline ou les messages de commit comme preuve.

### Code Changes Philosophy

- **Simplicity First** — le changement le plus simple possible pour atteindre l'objectif.
- **Minimal Impact** — ne modifier que le nécessaire.
- **Root Cause Focus** — corriger la cause racine, pas de fix temporaire.
- Éviter la sur-ingénierie.
- En corrigeant un bug, ajouter un test de non-régression.

## Coding Guidelines

- **Style**: PEP 8. Type hints partout (signatures de fonctions, modèles Pydantic pour les schémas d'entrée/sortie).
- **Concurrency**: privilégier `async`/`await` (natif FastAPI/Starlette) plutôt que du code bloquant dans les routes/services appelant des API externes.
- **Documentation**: docstrings courtes pour les fonctions/services publics non triviaux. Commentaires inline minimaux — ne pas reformuler ce que le code dit déjà ; ne pas les traiter comme spécification lors d'une revue, seul le code/tests font foi.
- **Erreurs**: pas d'`except:` nu — capturer des exceptions spécifiques ; utiliser `app/core/exceptions.py` pour les erreurs métier existantes plutôt que d'en recréer.
- **Optional handling**: typer explicitement avec `Optional[...]`/`| None`, préférer un retour anticipé (`if not x: return/raise`) plutôt que d'imbriquer les conditions.
- **Config/secrets**: jamais de clé/API key en dur — passer par `app/core/config.py` et les variables d'environnement (`.env`, jamais committé).

## Testing Rules

- Tests unitaires dans `tests/unit/` (un fichier `test_routes_*.py` par router, voir les fichiers existants pour les conventions de nommage et de mocking).
- Tests d'intégration dans `tests/integration/`.
- En ajoutant une route/un service : ajouter les tests correspondants dans le bon dossier, suivre le style des tests déjà présents (fixtures dans `conftest.py`).
- Ne pas lancer les tests soi-même — voir `CLAUDE.local.md`.

## Infrastructure

- **API externes**: Google Places API (autocomplete, photos, details) via `app/api/`, encapsulée par `app/services/places_service.py` / `autocomplete_service.py` / `photos_service.py`.
- **Base de données / Auth**: Supabase — accès via `app/services/supabase_service.py` et `app/core/database.py` ; auth JWT via `app/core/security.py`.
- **IA**: génération de contenu (trips, descriptions) via OpenAI, encapsulée dans `app/services/ai_service.py`.
- **Cache d'images**: stockage et cache côté serveur via `app/services/storage_service.py`.
- **Sessions de recherche**: token de session Google Places propagé entre autocomplete et place details (voir `commandes.md`, variable `SESSION`).

## Tools & Commands

- **Make** — voir `Makefile` pour toutes les cibles : `make install`, `make dev`, `make test`, `make test-unit`, `make test-integration`, `make test-file FILE=...`, `make test-one TEST=...`, `make import-all`, `make import-country country=...`.
- **Docker** — `Dockerfile` à la racine pour la conteneurisation.
- **gh** (GitHub CLI) — installé et authentifié ; utilisé pour PR/labels/secrets/variables (toujours avec accord préalable, voir `CLAUDE.local.md`).
- **commandes.md** — aide-mémoire de commandes et exemples curl pour ce projet.
