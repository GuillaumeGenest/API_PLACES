import os
from dotenv import load_dotenv
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Charger les variables d'environnement
load_dotenv()

def check_env():
    """Vérifie et charge toutes les variables d'environnement au démarrage"""
    get_api_key()
    get_openai_key()
    get_server_base_url()
    get_supabase_url()
    get_supabase_key()
    logger.info("✅ Toutes les variables d'environnement sont chargées")


def _get_env_variable(env_map: dict, label: str) -> str:
    """
    Fonction générique pour récupérer une variable d'environnement
    en fonction de ENVIRONMENT.
    """
    env = os.getenv("ENVIRONMENT", "production")

    key = env_map.get(env, env_map.get("production"))
    value = os.getenv(key)

    if not value:
        logger.error(f"{label} manquante pour l'environnement : {env}")
        raise ValueError(f"{label} n'est pas configurée pour l'environnement {env}")

    logger.info(f"{label} chargée pour l'environnement : {env}")
    return value


# MARK: - Google API KEY
def get_api_key():
    return _get_env_variable(
        {
            "development": "GOOGLE_API_KEY_DEV",
            "testing": "GOOGLE_API_KEY_TEST",
            "production": "GOOGLE_API_KEY_PROD",
        },
        "Clé API Google Places",
    )


# MARK: - OpenAI KEY
def get_openai_key():
    return _get_env_variable(
        {
            "development": "OPENAI_API_KEY_DEV",
            "testing": "OPENAI_API_KEY_TEST",
            "production": "OPENAI_API_KEY_PROD",
        },
        "Clé API OpenAI",
    )


# MARK: - Database URL
def get_database_url():
    return _get_env_variable(
        {
            "development": "DATABASE_URL_DEV",
            "testing": "DATABASE_URL_TEST",
            "production": "DATABASE_URL_PROD",
        },
        "DATABASE_URL",
    )


# MARK: - Server Base URL
def get_server_base_url():
    return _get_env_variable(
        {
            "development": "SERVER_BASE_URL_DEV",
            "testing": "SERVER_BASE_URL_TEST",
            "production": "SERVER_BASE_URL_PROD",
        },
        "SERVER_BASE_URL",
    )

def get_supabase_url():
    return _get_env_variable(
        {
            "development": "SUPABASE_BASE_URL_DEV",  # ✅
            "testing": "SUPABASE_BASE_URL_TEST",
            "production": "SUPABASE_BASE_URL_PROD",
        },
        "SUPABASE_URL",
    )

# MARK: - Supabase Key
def get_supabase_key():
    return _get_env_variable(
        {
            "development": "SUPABASE_API_KEY_DEV",  # ✅
            "testing": "SUPABASE_API_KEY_TEST",
            "production": "SUPABASE_API_KEY_PROD",
        },
        "SUPABASE_KEY",
    )