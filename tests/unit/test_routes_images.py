import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
import app.routers.images as images_module


class TestGetImages(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    # --- /images/place ---

    def test_get_image_by_name_success(self):
        with patch('app.routers.images.PhotosService') as MockService:
            instance = MockService.return_value
            instance.get_image_by_name = AsyncMock(return_value="http://example.com/photo.jpg")
            response = self.client.get("/images/place?place=Tour+Eiffel")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "http://example.com/photo.jpg")

    def test_get_image_by_name_not_found(self):
        with patch('app.api.API_Photos.get_url_image_from_wikipedia', new_callable=AsyncMock, return_value=None):
            response = self.client.get("/images/place?place=Inconnu")
            self.assertEqual(response.status_code, 404)
            self.assertIn("IMAGE_NOT_FOUND", response.json()["error"])

    # --- /images/place_and_address ---

    def test_get_image_by_place_and_address_success(self):
        with patch.object(images_module.places_service, 'get_place_id', new_callable=AsyncMock, return_value="test_place_id"), \
             patch.object(images_module.photos_service, 'get_image_by_place_id', new_callable=AsyncMock, return_value="http://example.com/photo.jpg"), \
             patch('app.routers.images.is_stored', return_value=False), \
             patch('app.routers.images.get_storage_url', return_value="http://localhost:8000/images/storage/caches/test_place_id.jpg"), \
             patch('app.routers.images.download_and_store', new_callable=AsyncMock, return_value="http://localhost:8000/images/storage/caches/test_place_id.jpg"):
            response = self.client.get("/images/place_and_address?place_name=Tour+Eiffel&address=Paris")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "http://localhost:8000/images/storage/caches/test_place_id.jpg")

    def test_get_image_by_place_and_address_cache_hit(self):
        with patch.object(images_module.places_service, 'get_place_id', new_callable=AsyncMock, return_value="test_place_id"), \
             patch('app.routers.images.is_stored', return_value=True), \
             patch('app.routers.images.get_storage_url', return_value="http://localhost:8000/images/storage/caches/test_place_id.jpg"):
            response = self.client.get("/images/place_and_address?place_name=Tour+Eiffel&address=Paris")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "http://localhost:8000/images/storage/caches/test_place_id.jpg")

    def test_get_image_by_place_and_address_place_not_found(self):
        with patch.object(images_module.places_service, 'get_place_id', new_callable=AsyncMock, return_value=None):
            response = self.client.get("/images/place_and_address?place_name=Inconnu")
            self.assertEqual(response.status_code, 400)
            self.assertIn("PLACE_NOT_FOUND", response.json()["error"])

    def test_get_image_by_place_and_address_no_photo(self):
        with patch.object(images_module.places_service, 'get_place_id', new_callable=AsyncMock, return_value="test_place_id"), \
             patch.object(images_module.photos_service, 'get_image_by_place_id', new_callable=AsyncMock, return_value=None), \
             patch('app.routers.images.is_stored', return_value=False), \
             patch('app.routers.images.get_storage_url', return_value="http://localhost:8000/images/storage/caches/test_place_id.jpg"), \
             patch('app.routers.images.download_and_store', new_callable=AsyncMock, return_value=None):
            response = self.client.get("/images/place_and_address?place_name=Tour+Eiffel&address=Paris")
            self.assertEqual(response.status_code, 404)
            self.assertIn("IMAGE_NOT_FOUND", response.json()["error"])

    # --- /images/id ---

    def test_get_image_by_id_missing(self):
        response = self.client.get("/images/id?place_id=")
        self.assertEqual(response.status_code, 400)
        self.assertIn("PLACE_ID_MISSING", response.json()["error"])

    def test_get_image_by_id_success(self):
        with patch.object(images_module.photos_service, 'get_image_by_place_id', new_callable=AsyncMock, return_value="http://example.com/photo.jpg"), \
             patch('app.routers.images.is_stored', return_value=False), \
             patch('app.routers.images.get_storage_url', return_value="http://localhost:8000/images/storage/caches/test_place_id.jpg"), \
             patch('app.routers.images.download_and_store', new_callable=AsyncMock, return_value="http://localhost:8000/images/storage/caches/test_place_id.jpg"):
            response = self.client.get("/images/id?place_id=test_place_id")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "http://localhost:8000/images/storage/caches/test_place_id.jpg")

    def test_get_image_by_id_cache_hit(self):
        with patch('app.routers.images.is_stored', return_value=True), \
             patch('app.routers.images.get_storage_url', return_value="http://localhost:8000/images/storage/caches/test_place_id.jpg"):
            response = self.client.get("/images/id?place_id=test_place_id")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "http://localhost:8000/images/storage/caches/test_place_id.jpg")

    def test_get_image_by_id_no_photo(self):
        with patch.object(images_module.photos_service, 'get_image_by_place_id', new_callable=AsyncMock, return_value=None), \
             patch('app.routers.images.is_stored', return_value=False), \
             patch('app.routers.images.get_storage_url', return_value="http://localhost:8000/images/storage/caches/test_place_id.jpg"), \
             patch('app.routers.images.download_and_store', new_callable=AsyncMock, return_value=None):
            response = self.client.get("/images/id?place_id=test_place_id")
            self.assertEqual(response.status_code, 404)
            self.assertIn("IMAGE_NOT_FOUND", response.json()["error"])


if __name__ == '__main__':
    unittest.main(verbosity=2)