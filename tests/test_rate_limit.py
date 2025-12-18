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


def test_rate_limiter_allows_10_req_sec_with_api_key():
    mock_response = MagicMock()
    mock_response.json.return_value = {"esearchresult": {"idlist": [], "count": "0"}}

    with patch('requests.get', return_value=mock_response):
        pubmed = PubMed(api_key="test_key")

        start = time.time()
        for _ in range(10):
            pubmed.search("test")
        elapsed = time.time() - start

        # 10 requests at 10 req/sec = ~1 second (not 3+ seconds)
        assert elapsed < 1.5


def test_search_and_fetch_respects_rate_limit():
    search_response = MagicMock()
    search_response.json.return_value = {"esearchresult": {"idlist": ["123"], "count": "1"}}

    fetch_response = MagicMock()
    fetch_response.text = """<?xml version="1.0"?>
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation><PMID>123</PMID><Article><ArticleTitle>Test</ArticleTitle><Abstract><AbstractText>Abstract</AbstractText></Abstract><AuthorList><Author><LastName>Doe</LastName><ForeName>John</ForeName></Author></AuthorList><Journal><Title>Test Journal</Title></Journal></Article></MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>"""

    with patch('requests.get', side_effect=[search_response, fetch_response]) as mock_get:
        pubmed = PubMed()

        start = time.time()
        pubmed.search_and_fetch("test")
        elapsed = time.time() - start

        # 2 requests at 3 req/sec = at least 0.33s between them
        assert mock_get.call_count == 2
        assert elapsed >= 0.3
