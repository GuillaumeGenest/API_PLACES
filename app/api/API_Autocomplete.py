import httpx
from typing import Optional
from app.core.config import get_api_key
from app.core.logger import setup_logger

logger = setup_logger(__name__)

GOOGLE_API_KEY = get_api_key()


async def get_autocomplete_predictions(
    input: str,
    session_token: Optional[str] = None,
    language: str = "fr"
) -> list:
    """
    Nouvelle API Google Places Autocomplete (New).
    - session_token optionnel : Android l'envoie, iOS non
    - FieldMask limité : uniquement les champs nécessaires → optimisation coût
    - Minimum 4 caractères géré en amont dans le router
    """
    logger.info(f"GOOGLE | Autocomplete — input={input} has_session={session_token is not None}")

    payload = {
        "input": input,
        "languageCode": language,
    }

    if session_token:
        payload["sessionToken"] = session_token

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ",".join([
            "suggestions.placePrediction.placeId",
            "suggestions.placePrediction.text.text",
            "suggestions.placePrediction.structuredFormat.mainText.text",
            "suggestions.placePrediction.structuredFormat.secondaryText.text"
        ])
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://places.googleapis.com/v1/places:autocomplete",
                json=payload,
                headers=headers
            )

        if response.status_code != 200:
            logger.error(f"GOOGLE | Autocomplete erreur — status={response.status_code} body={response.text}")
            return []

        data = response.json()
        predictions = []

        for s in data.get("suggestions", []):
            place = s.get("placePrediction")
            if not place:
                continue
            predictions.append({
                "place_id":       place.get("placeId"),
                "name":           place.get("text", {}).get("text"),
                "main_text":      place.get("structuredFormat", {}).get("mainText", {}).get("text"),
                "secondary_text": place.get("structuredFormat", {}).get("secondaryText", {}).get("text")
            })

        logger.info(f"GOOGLE | Autocomplete — {len(predictions)} résultats pour input={input}")
        return predictions

    except Exception as e:
        logger.error(f"GOOGLE | Autocomplete exception — input={input} error={e}")
        return []