import os
from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
from app.core.config import *
from app.core.logger import setup_logger
from openai import AsyncOpenAI
from datetime import datetime
import json
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import uuid
from app.api.API_Photos import get_url_image_from_wikipedia, get_url_image_from_google

logger = setup_logger(__name__)

client = AsyncOpenAI(api_key=get_openai_key())

async def generate_attraction(
    place_name: str,
    full_address: Optional[str] = None,
    category_name: str = "autre"
):
    full_query = f"{place_name}, {full_address}" if full_address else place_name
    logger.info(f"OPENAI | Génération attraction — query={full_query} category={category_name}")
    try:
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
      "rating": float ou null,
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

        logger.debug(f"OPENAI | Appel API — modèle=gpt-4.1-mini query={full_query}")
        response = await client.responses.create(
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
        logger.debug(f"OPENAI | Réponse reçue — longueur={len(response.output_text)} chars")

        # Nettoyage du texte
        clean_text = response.output_text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`").replace("json", "", 1).strip()

        data = json.loads(clean_text)

        formatted_attractions = []
        for place in data.get("attraction", []):
            logger.debug(f"WIKIPEDIA | Recherche image — name={place.get('name', place_name)}")
            photo_url = await get_url_image_from_wikipedia(place.get("name", place_name))

            opening_hours = place.get('opening_hours', [])

            raw_rating = place.get('rating')
            try:
                rating = float(raw_rating) if raw_rating is not None else None
            except (ValueError, TypeError):
                rating = None

            attraction = {
                'name': place.get('name', 'Non spécifié'),
                'address': place.get('address', 'Non spécifiée'),
                'place_id': f"ai_{uuid.uuid4().hex}",
                'latitude': place.get('latitude'),
                'longitude': place.get('longitude'),
                'rating': rating,
                'user_ratings_total': place.get('user_ratings_total', 0),
                'photo_urls': [photo_url] if photo_url else [],
                'website': place.get('website', 'Non disponible'),
                'google_maps_url': "Non disponible",
                'phone': place.get('phone', 'Non disponible'),
                'description': place.get('description'),
                'opening_hours': opening_hours,
                'category': category_name
            }
            formatted_attractions.append(attraction)

        logger.info(f"OPENAI | Attraction générée — name={formatted_attractions[0]['name'] if formatted_attractions else 'N/A'}")
        return {"attraction": formatted_attractions}

    except json.JSONDecodeError as e:
        logger.error(f"OPENAI | Erreur parsing JSON — query={full_query} error={e}")
        return None
    except Exception as e:
        logger.error(f"OPENAI | Erreur inattendue generate_attraction — query={full_query} error={type(e).__name__}: {e}")
        return None


async def generate_description(
    place_name: str,
    full_address: Optional[str] = None
) -> Optional[str]:
    full_query = f"{place_name}, {full_address}" if full_address else place_name
    logger.info(f"OPENAI | Génération description — query={full_query}")

    try:
        prompt = f"""
Donne une description factuelle et concise du lieu suivant : {full_query}.
La description doit tenir en **maximum 3 lignes**.
Retourne UNIQUEMENT la description en texte, sans JSON ni explication supplémentaire.
"""

        logger.debug(f"OPENAI | Appel API — modèle=gpt-4.1-mini query={full_query}")
        response = await client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": "Tu es un assistant spécialisé en tourisme."},
                {"role": "user", "content": prompt}
            ]
        )

        description = response.output_text.strip()
        logger.info(f"OPENAI | Description générée — query={full_query} longueur={len(description)} chars")
        return description

    except Exception as e:
        logger.error(f"OPENAI | Erreur inattendue generate_description — query={full_query} error={type(e).__name__}: {e}")
        return None