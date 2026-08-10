from unittest.mock import patch
from app.services.fetch_news import fetch_and_store_news


def test_fetch_handles_request_failure_gracefully(app):
    with patch("app.services.fetch_news.requests.get") as mock_get:
        mock_get.side_effect = Exception("Simulated network failure")
        count = fetch_and_store_news()
        assert count == 0