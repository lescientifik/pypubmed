import time
from unittest.mock import patch, MagicMock
import pytest
from pypubmed import PubMed


@pytest.mark.slow
def test_rate_limit_respects_3_requests_per_second():
    mock_response = MagicMock()
    mock_response.json.return_value = {"esearchresult": {"idlist": [], "count": "0"}}

    with patch('requests.get', return_value=mock_response):
        pubmed = PubMed()
        n_calls = 4

        start = time.time()
        for _ in range(n_calls):
            pubmed.search("test")
        elapsed = time.time() - start

        # 4 calls = 3 intervals at 3 req/sec = 1 second minimum
        min_time = (n_calls - 1) / 3
        assert elapsed >= min_time * 0.9  # small tolerance
