from app.api.API_Photos import (
    get_url_image_from_wikipedia,
    get_url_image_from_google
)
from typing import Optional


class PhotosService:

    def get_image_by_name(self, place_name: str) -> Optional[str]:
        return get_url_image_from_wikipedia(place_name)

    def get_image_by_place_id(self, place_id: str) -> Optional[str]:
        return get_url_image_from_google(place_id)