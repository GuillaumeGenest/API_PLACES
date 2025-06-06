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


load_dotenv()
OPENAI_API_KEY = get_openai_key()
print(f"Clé OPENAPI utilisée pour les tests: {OPENAI_API_KEY}")  # Version simple

client = OpenAI()


def generate_city_trip(
    ville: str,
    date_debut: str,
    date_fin: str
):

#def lieux_a_visiter(
#    ville: str = Query(..., description="Nom de la ville ou du lieu"),
#    date_debut: str = Query(..., description="Date de début au format YYYY-MM-DD"),
#    date_fin: str = Query(..., description="Date de fin au format YYYY-MM-DD")
#):
    try:
        # Vérification cohérence des dates
        debut = datetime.strptime(date_debut, "%Y-%m-%d")
        fin = datetime.strptime(date_fin, "%Y-%m-%d")
        if debut > fin:
            return JSONResponse(status_code=400, content={"error": "La date de début doit être antérieure ou égale à la date de fin."})

        # Nouveau prompt avec planification demandée au modèle
        prompt = (
            f"Je fais un voyage à {ville} du {date_debut} au {date_fin}.\n"
            f"Donne-moi une liste de 10 lieux touristiques à visiter pendant ce séjour.\n"
            f"Pour chaque lieu, indique : le nom, l'adresse, la date précise de visite, "
            f"et si c'est prévu pour le matin ou l'après-midi.\n"
            f"Formate la réponse uniquement au format JSON comme ceci :\n"
            f'[{{"nom": "Nom du lieu", "adresse": "Adresse", "date_estimee": "YYYY-MM-DD", "moment": "matin" ou "après-midi"}}, ...]'
        )
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
            {
                "role": "system",
                "content": "Tu es un assistant de voyage."
            },
            {
                "role": "user",
                "content": prompt
            }
            ]
        )

        input=[
        {
            "role": "system",
            "content": "Tu es un assistant de voyage."
        },
        {
            "role": "user",
            "content": "prompt"
        }
        ]

        print(response.output_text)
        data = json.loads(response.output_text)
        #data = JSONResponse(content=lieux)
        #print(data.body.decode("utf-8"))
        # 3. Tu renvoies cette liste dans ta réponse d'API
        #return JSONResponse(content=lieux)

       
        # content = response['choices'][0]['message']['content']
        # lieux = json.loads(content)

        # if not isinstance(lieux, list) or len(lieux) != 10:
        #     return JSONResponse(status_code=500, content={"error": "Réponse inattendue de l'API OpenAI."})

        #return JSONResponse(content=lieux)
        return data
    except ValueError:
        print("status_code=400")

    except Exception as e:
         print("status_code=500", str(e))



def generate_road_trip(
    region: str,
    date_debut: str,
    date_fin: str
):




#def lieux_a_visiter(
#    ville: str = Query(..., description="Nom de la ville ou du lieu"),
#    date_debut: str = Query(..., description="Date de début au format YYYY-MM-DD"),
#    date_fin: str = Query(..., description="Date de fin au format YYYY-MM-DD")
#):
    try:
        # Vérification cohérence des dates
        debut = datetime.strptime(date_debut, "%Y-%m-%d")
        fin = datetime.strptime(date_fin, "%Y-%m-%d")
        if debut > fin:
            return JSONResponse(status_code=400, content={"error": "La date de début doit être antérieure ou égale à la date de fin."})
        print(f"Je fais un road trip en {region} du {date_debut} au {date_fin}.")
        # Nouveau prompt avec planification demandée au modèle
        prompt = (
            f"Je fais un road trip en {region} du {date_debut} au {date_fin}.\n"
            f"Donne-moi une liste de 10 lieux touristiques ou ville à visiter pendant ce séjour.\n"
            f"Pour chaque lieu, indique : le nom, l'adresse, la date précise de visite, "
            f"Formate la réponse uniquement au format JSON comme ceci :\n"
            f'[{{"nom": "Nom du lieu", "adresse": "Adresse", "date_estimee": "YYYY-MM-DD"}}, ...]'
        )
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
            {
                "role": "system",
                "content": "Tu es un assistant de voyage."
            },
            {
                "role": "user",
                "content": prompt
            }
            ]
        )

        input=[
        {
            "role": "system",
            "content": "Tu es un assistant de voyage."
        },
        {
            "role": "user",
            "content": "prompt"
        }
        ]

        print(response.output_text)
        data = json.loads(response.output_text)
        #data = JSONResponse(content=lieux)
        #print(data.body.decode("utf-8"))
        # 3. Tu renvoies cette liste dans ta réponse d'API
        #return JSONResponse(content=lieux)

       
        # content = response['choices'][0]['message']['content']
        # lieux = json.loads(content)

        # if not isinstance(lieux, list) or len(lieux) != 10:
        #     return JSONResponse(status_code=500, content={"error": "Réponse inattendue de l'API OpenAI."})

        #return JSONResponse(content=lieux)
        return data
    except ValueError:
        print("status_code=400")

    except Exception as e:
         print("status_code=500", str(e))