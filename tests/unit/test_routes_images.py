import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app


class TestGetImages(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    # --- /images/place ---

    def test_get_image_by_name_success(self):
        with patch('app.routers.images.PhotosService') as MockService:
            instance = MockService.return_value
            instance.get_image_by_name.return_value = "http://example.com/photo.jpg"
            response = self.client.get("/images/place?place=Tour+Eiffel")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "http://example.com/photo.jpg")

    def test_get_image_by_name_not_found(self):
        with patch('app.routers.images.PhotosService') as MockService:
            instance = MockService.return_value
            instance.get_image_by_name.return_value = None
            response = self.client.get("/images/place?place=Inconnu")
            self.assertEqual(response.status_code, 404)
            self.assertIn("IMAGE_NOT_FOUND", response.json()["error"])

    # --- /images/place_and_address ---

    def test_get_image_by_place_and_address_success(self):
        with patch('app.routers.images.PlacesService') as MockPlaces, \
             patch('app.routers.images.PhotosService') as MockPhotos:
            MockPlaces.return_value.get_place_id.return_value = "test_place_id"
            MockPhotos.return_value.get_image_by_place_id.return_value = "http://example.com/photo.jpg"
            response = self.client.get("/images/place_and_address?place_name=Tour+Eiffel&address=Paris")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "http://example.com/photo.jpg")

    def test_get_image_by_place_and_address_place_not_found(self):
        with patch('app.routers.images.PlacesService') as MockPlaces, \
             patch('app.routers.images.PhotosService'):
            MockPlaces.return_value.get_place_id.return_value = None
            response = self.client.get("/images/place_and_address?place_name=Inconnu")
            self.assertEqual(response.status_code, 400)
            self.assertIn("PLACE_NOT_FOUND", response.json()["error"])

    def test_get_image_by_place_and_address_no_photo(self):
        with patch('app.routers.images.PlacesService') as MockPlaces, \
             patch('app.routers.images.PhotosService') as MockPhotos:
            MockPlaces.return_value.get_place_id.return_value = "test_place_id"
            MockPhotos.return_value.get_image_by_place_id.return_value = None
            response = self.client.get("/images/place_and_address?place_name=Tour+Eiffel&address=Paris")
            self.assertEqual(response.status_code, 404)
            self.assertIn("IMAGE_NOT_FOUND", response.json()["error"])

    # --- /images/id ---

    def test_get_image_by_id_missing(self):
        response = self.client.get("/images/id?place_id=")
        self.assertEqual(response.status_code, 400)
        self.assertIn("PLACE_ID_MISSING", response.json()["error"])

    def test_get_image_by_id_success(self):
        with patch('app.routers.images.PhotosService') as MockService:
            instance = MockService.return_value
            instance.get_image_by_place_id.return_value = "http://example.com/photo.jpg"
            response = self.client.get("/images/id?place_id=test_place_id")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "http://example.com/photo.jpg")

    def test_get_image_by_id_no_photo(self):
        with patch('app.routers.images.PhotosService') as MockService:
            instance = MockService.return_value
            instance.get_image_by_place_id.return_value = None
            response = self.client.get("/images/id?place_id=test_place_id")
            self.assertEqual(response.status_code, 404)
            self.assertIn("IMAGE_NOT_FOUND", response.json()["error"])


if __name__ == '__main__':
    unittest.main(verbosity=2)