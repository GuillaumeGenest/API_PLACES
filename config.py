import os
from dotenv import load_dotenv

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
        raise Exception(f"La clé API Google Places n'est pas configurée pour l'environnement {env}")
        
    return api_key


def get_openai_key():
    """
    Retourne la clé API OpenAI en fonction de l'environnement actuel
    """
    env = os.getenv('ENVIRONMENT', 'production')

    # Récupérer l'environnement depuis la variable d'environnement
    if env == 'development':
        api_key = os.getenv('OPENAI_API_DEV')
    elif env == 'testing':
        api_key = os.getenv('OPENAI_API_DEV')
    else:  # production par défaut
        api_key = os.getenv('OPENAI_API_KEY')
    
    # Vérification que la clé existe
    if not api_key:
        raise Exception(f"La clé API OPENAI n'est pas configurée pour l'environnement {env}") 
    return api_key