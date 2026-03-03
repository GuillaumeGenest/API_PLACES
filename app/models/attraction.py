from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class AttractionCategory(str, Enum):
    touristique = "touristique"
    nature = "nature"
    restaurant = "restaurant"
    autre = "autre"


class Attraction(BaseModel):
    name: str
    address: Optional[str] = None
    place_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    photo_urls: List[str] = []
    website: Optional[str] = None
    google_maps_url: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    opening_hours: Optional[List[str]] = None
    price_level: Optional[str] = None
    price_range: Optional[str] = None
    category: AttractionCategory = AttractionCategory.autre

    class Config:
        extra = "ignore"  # ignore les champs inconnus de l'API Google


class AttractionResponse(BaseModel):
    attraction: List[Attraction]


class SingleAttractionResponse(BaseModel):
    attraction: Attraction