"""Tests for retry logic - uses mocking for fast execution."""

from unittest.mock import Mock, patch

import pytest
import requests

from pypubmed import PubMed, APIError


@patch("pypubmed.client.time.sleep")  # Mock sleep to speed up tests
class TestRetryOnTransientError:
    """Test retry behavior on transient errors."""

    def test_retry_on_connection_error(self, mock_sleep):
        """Should retry on ConnectionError and succeed."""
        pubmed = PubMed()

        # Mock response for successful call
        success_response = Mock()
        success_response.status_code = 200
        success_response.raise_for_status = Mock()
        success_response.json.return_value = {
            "esearchresult": {"idlist": ["12345"], "count": "1"}
        }

        # First 2 calls fail, third succeeds
        pubmed._session.get = Mock(
            side_effect=[
                requests.ConnectionError("Network error"),
                requests.ConnectionError("Network error"),
                success_response,
            ]
        )

        result = pubmed.search("test", max_results=1)

        assert result.ids == ["12345"]
        assert pubmed._session.get.call_count == 3

    def test_retry_on_500_error(self, mock_sleep):
        """Should retry on 500 server error and succeed."""
        pubmed = PubMed()

        # Mock 500 error response
        error_response = Mock()
        error_response.status_code = 500
        error_response.raise_for_status = Mock(
            side_effect=requests.HTTPError("500 Server Error")
        )

        # Mock success response
        success_response = Mock()
        success_response.status_code = 200
        success_response.raise_for_status = Mock()
        success_response.json.return_value = {
            "esearchresult": {"idlist": ["12345"], "count": "1"}
        }

        pubmed._session.get = Mock(
            side_effect=[error_response, success_response]
        )

        result = pubmed.search("test", max_results=1)

        assert result.ids == ["12345"]
        assert pubmed._session.get.call_count == 2

    def test_retry_on_429_rate_limit(self, mock_sleep):
        """Should retry on 429 rate limit error."""
        pubmed = PubMed()

        # Mock 429 error response
        error_response = Mock()
        error_response.status_code = 429
        error_response.raise_for_status = Mock(
            side_effect=requests.HTTPError("429 Too Many Requests")
        )

        # Mock success response
        success_response = Mock()
        success_response.status_code = 200
        success_response.raise_for_status = Mock()
        success_response.json.return_value = {
            "esearchresult": {"idlist": ["12345"], "count": "1"}
        }

        pubmed._session.get = Mock(
            side_effect=[error_response, success_response]
        )

        result = pubmed.search("test", max_results=1)

        assert result.ids == ["12345"]
        assert pubmed._session.get.call_count == 2

    def test_no_retry_on_400_error(self, mock_sleep):
        """Should NOT retry on 400 client error."""
        pubmed = PubMed()

        error_response = Mock()
        error_response.status_code = 400
        error_response.raise_for_status = Mock(
            side_effect=requests.HTTPError("400 Bad Request")
        )

        pubmed._session.get = Mock(return_value=error_response)

        with pytest.raises(APIError):
            pubmed.search("test", max_results=1)

        # Should only try once, no retry
        assert pubmed._session.get.call_count == 1

    def test_max_retries_exceeded(self, mock_sleep):
        """Should raise after max retries exceeded."""
        pubmed = PubMed()

        pubmed._session.get = Mock(
            side_effect=requests.ConnectionError("Network error")
        )

        with pytest.raises(APIError, match="Network error"):
            pubmed.search("test", max_results=1)

        # Default 3 retries = 4 total attempts
        assert pubmed._session.get.call_count == 4
