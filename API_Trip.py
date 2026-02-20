import requests
import os

from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
from config import *
from openai import OpenAI
from datetime import datetime
import json
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import json
import uuid

load_dotenv()
OPENAI_API_KEY = get_openai_key()
print(f"Clé OPENAPI utilisée pour les tests: {OPENAI_API_KEY}")  # Version simple

client = OpenAI()


#def lieux_a_visiter(
#    ville: str = Query(..., description="Nom de la ville ou du lieu"),
#    date_debut: str = Query(..., description="Date de début au format YYYY-MM-DD"),
#    date_fin: str = Query(..., description="Date de fin au format YYYY-MM-DD")
#):
def generate_city_trip(ville: str, date_debut: str, date_fin: str):
    try:
        # Vérification cohérence des dates
        debut = datetime.strptime(date_debut, "%Y-%m-%d")
        fin = datetime.strptime(date_fin, "%Y-%m-%d")
        
        if debut > fin:
            raise HTTPException(
                status_code=400, 
                detail="La date de début doit être antérieure ou égale à la date de fin."
            )
        
        print(f"Visite de {ville} du {date_debut} au {date_fin}.")
        
        # Prompt optimisé
        prompt = (
            f"Génère un itinéraire de visite pour {ville} du {date_debut} au {date_fin}.\n"
            f"L'objectif est de visiter les principaux lieux touristiques de cette ville pendant cette période.\n\n"
            f"Fournis une liste de lieux touristiques à visiter (environ 10 à 15 lieux).\n\n"
            f"Chaque entrée doit contenir les champs suivants :\n"
            f"- nom : nom du lieu touristique\n"
            f"- adresse : adresse complète\n"
            f"- countryCode : code ISO du pays\n"
            f"- latitude\n"
            f"- longitude\n"
            f"- date (au format YYYY-MM-DDTHH:MM:SS, réparties entre le {date_debut} et le {date_fin})\n\n"
            f"Les dates doivent être réparties sur l'ensemble du séjour de manière cohérente.\n"
            f"Utilise des horaires réalistes : entre 09:00:00 et 19:00:00.\n"
            f'Le format de réponse doit être uniquement au format JSON, avec une clé principale : "lieux".'
        )
        
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Tu es un assistant de voyage expert. Tu réponds uniquement en JSON valide, sans texte supplémentaire."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        print("Réponse brute:", response.output_text)
         # Vérifier que la réponse n'est pas vide
        if not response.output_text or response.output_text.strip() == "":
            raise HTTPException(status_code=500, detail="La réponse de l'IA est vide")
        
        # Parse la réponse JSON
        clean_text = response.output_text.strip()

        # Si le texte commence par des ``` on nettoie
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`")
            clean_text = clean_text.replace("json", "", 1).strip()


        data = json.loads(clean_text)
        # Parse la réponse JSON
        
        # Transformation au format TripDTO pour les lieux
        lieux_dto = []
        for idx, lieu in enumerate(data.get("lieux", []), start=1):
            trip_dto = {
                "id": str(idx),
                "locationName": lieu.get("nom", ""),
                "locationAdress": lieu.get("adresse", ""),
                "countryCode": lieu.get("countryCode", ""),
                "latitude": lieu.get("latitude", 0.0),
                "longitude": lieu.get("longitude", 0.0),
                "date": lieu.get("date", date_debut)
            }
            lieux_dto.append(trip_dto)
        
        return {"lieux": lieux_dto}
        
    except ValueError as e:
        print(f"Erreur de format de date: {e}")
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    except json.JSONDecodeError as e:
        print(f"Erreur de parsing JSON: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du parsing de la réponse IA")
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

#def lieux_a_visiter(
#    ville: str = Query(..., description="Nom de la ville ou du lieu"),
#    date_debut: str = Query(..., description="Date de début au format YYYY-MM-DD"),
#    date_fin: str = Query(..., description="Date de fin au format YYYY-MM-DD")
#):

def generate_road_trip(city: str, date_start: str, date_end: str):
    try:
        # Vérification cohérence des dates
        debut = datetime.strptime(date_start, "%Y-%m-%d")
        fin = datetime.strptime(date_end, "%Y-%m-%d")
        if debut > fin:
            raise HTTPException(
                status_code=400, 
                detail="La date de début doit être antérieure ou égale à la date de fin."
            )
        print(f"Je fais un road trip en {city} du {date_start} au {date_end}.")
        # Nouveau prompt avec planification demandée au modèle

        prompt = (
            f"Génère un itinéraire de road trip à partir de la ville {city} du {date_start} au {date_end}.\n"
            f"L'objectif est de visiter plusieurs villes et lieux pendant cette période.\n\n"
            f"Fournis deux listes distinctes :\n"
            f'"villes" : les principales villes ou localités visitées (max 10).\n'
            f'"lieux" : une liste détaillée des lieux touristiques à visiter, avec plusieurs lieux possibles par ville.\n\n'
            f"Chaque entrée de ces listes doit contenir les champs suivants :\n"
            f"- nom : nom de la ville ou du lieu\n"
            f"- adresse : adresse complète ou zone géographique\n"
            f"- countryCode : code ISO du pays\n"
            f"- latitude\n"
            f"- longitude\n"
            f"- date (au format YYYY-MM-DDTHH:MM:SS, réparties entre le {date_start} et le {date_end} de manière cohérente selon l'ordre du trajet)\n\n"
            f"Les dates doivent être réparties sur l'ensemble du voyage, avec une progression géographique logique (pas de sauts incohérents).\n"
            f'Le format de réponse doit être uniquement au format JSON, avec les deux clés principales : "villes" et "lieux".'
        )

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Tu es un assistant de voyage expert. Tu réponds toujours en JSON valide."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
       # DÉBOGAGE : Afficher le type et le contenu de la réponse
        print(f"Type de response: {type(response)}")
        print(f"Attributs de response: {dir(response)}")
        print(f"Réponse brute (output_text): '{response.output_text}'")
        print(f"Longueur: {len(response.output_text) if response.output_text else 0}")
        
        # Vérifier que la réponse n'est pas vide
        if not response.output_text or response.output_text.strip() == "":            raise HTTPException(status_code=500, detail="La réponse de l'IA est vide")
        
        # Parse la réponse JSON
        clean_text = response.output_text.strip()

        # Si le texte commence par des ``` on nettoie
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`")
            clean_text = clean_text.replace("json", "", 1).strip()


        data = json.loads(clean_text)
        
        # Transformation au format TripDTO pour les villes
        villes_dto = []
        for idx, ville in enumerate(data.get("villes", []), start=1):
            trip_dto = {
                "id": str(idx),
                "locationName": ville.get("nom", ""),
                "locationAdress": ville.get("adresse", ""),
                "countryCode": ville.get("countryCode", ""),
                "latitude": ville.get("latitude", 0.0),
                "longitude": ville.get("longitude", 0.0),
                "date": ville.get("date", date_start)
            }
            villes_dto.append(trip_dto)
        
        # Transformation au format TripDTO pour les lieux touristiques
        lieux_dto = []
        id_counter = len(villes_dto) + 1
        for lieu in data.get("lieux", []):
            trip_dto = {
                "id": str(id_counter),
                "locationName": lieu.get("nom", ""),
                "locationAdress": lieu.get("adresse", ""),
                "countryCode": lieu.get("countryCode", ""),
                "latitude": lieu.get("latitude", 0.0),
                "longitude": lieu.get("longitude", 0.0),
                "date": lieu.get("date", date_start)
            }
            lieux_dto.append(trip_dto)
            id_counter += 1
        
        return {
            "villes": villes_dto,
            "lieux": lieux_dto
        }
        
    except ValueError as e:
        print(f"Erreur de format de date (ValueError): {e}")
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    except json.JSONDecodeError as e:
        print(f"Erreur de parsing JSON: {e}")
        print(f"Contenu reçu: '{response.output_text if 'response' in locals() else 'Pas de réponse'}'")
        raise HTTPException(status_code=500, detail="Erreur lors du parsing de la réponse IA")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur inattendue: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


def generate_ai_attraction(
    place_name: str,
    full_address: Optional[str] = None,
    category_name: str = "autre"
):
    try:
        # Préparer la requête complète
        full_query = f"{place_name}, {full_address}" if full_address else place_name

        prompt = f"""
Donne les informations factuelles du lieu suivant : {full_query}.

Retourne UNIQUEMENT un JSON valide avec EXACTEMENT cette structure :

{{
  "attraction": [
    {{
      "name": string,
      "address": string,
      "latitude": float ou null,
      "longitude": float ou null,
      "rating": float ou "Non notée",
      "user_ratings_total": integer,
      "website": string ou "Non disponible",
      "phone": string ou "Non disponible",
      "description": string ou null,
      "opening_hours": array de strings au format ["lundi: 09:00 – 00:00", ...] ou ["Lundi: Fermé", ...],
      "photo_url": string ou null
    }}
  ]
}}

Règles :
- Ne pas inventer de données précises si incertain
- Si inconnu → null ou "Non disponible"
- Ne retourner AUCUN texte hors JSON
- Donne une photo représentative du lieu sous forme d'URL si possible
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Tu es un assistant spécialisé en données touristiques. Réponds uniquement en JSON valide."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Nettoyage du texte
        clean_text = response.output_text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`").replace("json", "", 1).strip()

        data = json.loads(clean_text)

        # Formatage final
        formatted_attractions = []
        for place in data.get("attraction", []):
            # S'assurer que opening_hours est bien une liste de chaînes
            opening_hours = place.get("opening_hours")
            if not isinstance(opening_hours, list):
                opening_hours = None

            attraction = {
                'name': place.get('name', 'Non spécifié'),
                'address': place.get('address', 'Non spécifiée'),
                'place_id': f"ai_{uuid.uuid4().hex}",  # faux place_id interne
                'latitude': place.get('latitude'),
                'longitude': place.get('longitude'),
                'rating': place.get('rating', 'Non notée'),
                'user_ratings_total': place.get('user_ratings_total', 0),
                'photo_urls': [place.get('photo_url')] if place.get('photo_url') else [],
                'website': place.get('website', 'Non disponible'),
                'google_maps_url': "Non disponible",
                'phone': place.get('phone', 'Non disponible'),
                'description': place.get('description'),
                'opening_hours': opening_hours,
                'category': category_name
            }

            formatted_attractions.append(attraction)

        return {"attraction": formatted_attractions}

    except Exception as e:
        print(f"Erreur IA: {e}")
        return None