import time
from unittest.mock import patch, MagicMock
from pypubmed import PubMed


def test_rate_limiter_delays_when_too_fast():
    mock_response = MagicMock()
    mock_response.json.return_value = {"esearchresult": {"idlist": [], "count": "0"}}

    with patch('requests.get', return_value=mock_response):
        pubmed = PubMed()

        start = time.time()
        for _ in range(4):
            pubmed.search("test")
        elapsed = time.time() - start

        # 4 requests at 3 req/sec = at least 1 second
        assert elapsed >= 1.0


def test_rate_limiter_does_not_delay_when_slow_enough():
    mock_response = MagicMock()
    mock_response.json.return_value = {"esearchresult": {"idlist": [], "count": "0"}}

    with patch('requests.get', return_value=mock_response):
        pubmed = PubMed()

        start = time.time()
        pubmed.search("test")
        time.sleep(0.4)  # wait longer than 0.33s (1/3 sec)
        pubmed.search("test")
        elapsed = time.time() - start

        # Should be ~0.4s, not 0.4s + rate limit delay
        assert elapsed < 0.6
