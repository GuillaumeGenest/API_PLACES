import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from app.api.API_Places_AI import generate_attraction


def _mock_openai_response(attraction_fields: dict):
    payload = {"attraction": [{"name": "Lieu Test", "address": "Quelque part", **attraction_fields}]}
    mock_response = MagicMock()
    mock_response.output_text = json.dumps(payload)
    return mock_response


class TestGenerateAttractionRatingNormalization(unittest.TestCase):

    def _run(self, mock_response):
        with patch('app.api.API_Places_AI.client') as mock_client, \
                patch('app.api.API_Places_AI.get_url_image_from_wikipedia', new_callable=AsyncMock, return_value=None):
            mock_client.responses.create = AsyncMock(return_value=mock_response)
            return asyncio.run(generate_attraction("Lieu Test"))

    def test_missing_rating_normalizes_to_none(self):
        result = self._run(_mock_openai_response({}))
        self.assertIsNone(result["attraction"][0]["rating"])

    def test_non_numeric_rating_normalizes_to_none(self):
        result = self._run(_mock_openai_response({"rating": "Non notée"}))
        self.assertIsNone(result["attraction"][0]["rating"])

    def test_numeric_rating_is_preserved_as_float(self):
        result = self._run(_mock_openai_response({"rating": 4.5}))
        self.assertEqual(result["attraction"][0]["rating"], 4.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
