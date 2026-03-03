import os
from dotenv import load_dotenv
from app.core.logger import setup_logger
logger = setup_logger(__name__)
# Charger les variables d'environnement
load_dotenv()



# MARK: - get_api_key
# Permet de récuper l'API KEY correspond à l'environnement 

def get_api_key():
    """
    Retourne la clé API Google Places en fonction de l'environnement actuel
    """
    env = os.getenv('ENVIRONMENT', 'production')

    # Récupérer l'environnement depuis la variable d'environnement
    if env == 'development':
        api_key = os.getenv('GOOGLE_API_KEY_DEV')
    elif env == 'testing':
        api_key = os.getenv('GOOGLE_API_KEY_TEST')
    else:  # production par défaut
        api_key = os.getenv('GOOGLE_API_KEY')
    
    # Vérification que la clé existe
    if not api_key:
        logger.error(f"Clé API Google manquante pour l'environnement : {env}")
        raise Exception(f"La clé API Google Places n'est pas configurée pour l'environnement {env}")
    logger.info(f"Clé API Google chargée pour l'environnement : {env}")
    return api_key


def get_openai_key():
    """
    Retourne la clé API OpenAI en fonction de l'environnement actuel
    """
    env = os.getenv('ENVIRONMENT', 'production')

    # Récupérer l'environnement depuis la variable d'environnement
    if env == 'development':
        api_key = os.getenv('OPENAI_API_KEY_DEV')
    elif env == 'testing':
        api_key = os.getenv('OPENAI_API_KEY_TEST')
    else:  # production par défaut
        api_key = os.getenv('OPENAI_API_KEY')
    
    # Vérification que la clé existe
    if not api_key:
        logger.error(f"Clé API OPENAI manquante pour l'environnement : {env}")
        raise Exception(f"La clé API OPENAI n'est pas configurée pour l'environnement {env}") 
    logger.debug(f"Clé API OPENAI chargée pour l'environnement : {env}")
    return api_key

#"""
#Retourne l'URL de connexion PostgreSQL en fonction de l'environnement actuel
#"""
def get_database_url():
    env = os.getenv('ENVIRONMENT', 'production')

    if env == 'development':
        db_url = os.getenv('DATABASE_URL_DEV')
    elif env == 'testing':
        db_url = os.getenv('DATABASE_URL_TEST')
    else:  # production par défaut
        db_url = os.getenv('DATABASE_URL')

    if not db_url:
        logger.error(f"La base de données n'est pas configurée pour l'environnement: {env}")
        raise Exception(f"La base de données n'est pas configurée pour l'environnement {env}")
    logger.info(f"La base de données est configurée pour l'environnement : {env}")
    return db_url