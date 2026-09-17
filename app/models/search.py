from pydantic import BaseModel
from typing import Optional


class AutocompletePrediction(BaseModel):
    place_id: Optional[str] = None
    name: Optional[str] = None
    main_text: Optional[str] = None
    secondary_text: Optional[str] = None


class SearchCoordinatesResponse(BaseModel):
    place_id: Optional[str] = None
    formatted_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_code: Optional[str] = None
