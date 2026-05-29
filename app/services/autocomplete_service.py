from typing import Optional
from app.api.API_Autocomplete import get_autocomplete_predictions
from app.core.logger import setup_logger

logger = setup_logger(__name__)


class AutocompleteService:

    async def autocomplete(
        self,
        input: str,
        session_token: Optional[str] = None,
        language: str = "fr"
    ) -> list:
        logger.info(f"SERVICE | Autocomplete — input={input}")
        return await get_autocomplete_predictions(input, session_token, language)