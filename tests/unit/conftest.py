import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_database():
    with patch('app.services.country_info_service.SessionLocal') as mock:
        mock.return_value = MagicMock()
        yield mock