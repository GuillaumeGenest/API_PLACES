import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import unittest
from unittest.mock import patch, AsyncMock
from app.services.ai_service import AIService
from app.services import ai_cache


class TestAIServiceDescriptionCache(unittest.TestCase):

    def setUp(self):
        ai_cache.clear()
        self.service = AIService()

    def test_generate_description_caches_result(self):
        with patch('app.services.ai_service.generate_description', new_callable=AsyncMock, return_value="Une description.") as mock_generate:
            first = asyncio.run(self.service.generate_description("Tour Eiffel", "Paris"))
            second = asyncio.run(self.service.generate_description("Tour Eiffel", "Paris"))
            self.assertEqual(first, "Une description.")
            self.assertEqual(second, "Une description.")
            mock_generate.assert_called_once()

    def test_generate_description_cache_key_ignores_case_and_spacing(self):
        with patch('app.services.ai_service.generate_description', new_callable=AsyncMock, return_value="Une description.") as mock_generate:
            asyncio.run(self.service.generate_description("Tour Eiffel", "Paris"))
            asyncio.run(self.service.generate_description("  tour eiffel  ", "PARIS"))
            mock_generate.assert_called_once()

    def test_generate_description_does_not_cache_failure(self):
        with patch('app.services.ai_service.generate_description', new_callable=AsyncMock, return_value=None) as mock_generate:
            asyncio.run(self.service.generate_description("LieuInexistant"))
            asyncio.run(self.service.generate_description("LieuInexistant"))
            self.assertEqual(mock_generate.call_count, 2)


class TestAIServiceAttractionCache(unittest.TestCase):

    def setUp(self):
        ai_cache.clear()
        self.service = AIService()

    def test_generate_attraction_caches_result(self):
        attraction_payload = {"attraction": [{"name": "Tour Eiffel"}]}
        with patch('app.services.ai_service.generate_attraction', new_callable=AsyncMock, return_value=attraction_payload) as mock_generate:
            first = asyncio.run(self.service.generate_attraction("Tour Eiffel", "Paris", "touristique"))
            second = asyncio.run(self.service.generate_attraction("Tour Eiffel", "Paris", "touristique"))
            self.assertEqual(first, attraction_payload)
            self.assertEqual(second, attraction_payload)
            mock_generate.assert_called_once()

    def test_generate_attraction_different_category_is_not_a_cache_hit(self):
        attraction_payload = {"attraction": [{"name": "Tour Eiffel"}]}
        with patch('app.services.ai_service.generate_attraction', new_callable=AsyncMock, return_value=attraction_payload) as mock_generate:
            asyncio.run(self.service.generate_attraction("Tour Eiffel", "Paris", "touristique"))
            asyncio.run(self.service.generate_attraction("Tour Eiffel", "Paris", "restaurant"))
            self.assertEqual(mock_generate.call_count, 2)

    def test_generate_attraction_does_not_cache_failure(self):
        with patch('app.services.ai_service.generate_attraction', new_callable=AsyncMock, return_value=None) as mock_generate:
            asyncio.run(self.service.generate_attraction("LieuInexistant"))
            asyncio.run(self.service.generate_attraction("LieuInexistant"))
            self.assertEqual(mock_generate.call_count, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
