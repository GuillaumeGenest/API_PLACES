import requests
import os

from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
from app.core.config import *
from openai import OpenAI
from datetime import datetime
import json
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import json
import uuid

# Nouveau
from app.api.API_Photos import get_url_image_from_wikipedia, get_url_image_from_google

load_dotenv()
OPENAI_API_KEY = get_openai_key()
print(f"Clé OPENAPI utilisée pour les tests: {OPENAI_API_KEY}")  # Version simple

client = OpenAI()


def generate_attraction(
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
            photo_url = get_url_image_from_wikipedia(place.get("name", place_name))
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

def generate_description(
    place_name: str,
    full_address: Optional[str] = None
) -> Optional[str]:
    try:
        full_query = f"{place_name}, {full_address}" if full_address else place_name

        prompt = f"""
Donne une description factuelle et concise du lieu suivant : {full_query}.
La description doit tenir en **maximum 3 lignes**.
Retourne UNIQUEMENT la description en texte, sans JSON ni explication supplémentaire.
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": "Tu es un assistant spécialisé en tourisme."},
                {"role": "user", "content": prompt}
            ]
        )

        description = response.output_text.strip()
        return description

    except Exception as e:
        print(f"Erreur IA: {e}")
        return None