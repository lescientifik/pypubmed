"""Tests for caching functionality."""

from unittest.mock import Mock, patch

import pytest

from pypubmed import PubMed


# Task 1: cache parameter
def test_cache_disabled_by_default():
    pubmed = PubMed()
    assert pubmed.cache is False


def test_cache_can_be_enabled():
    pubmed = PubMed(cache=True)
    assert pubmed.cache is True


# Task 2: cache stores articles
def test_cache_stores_articles_after_fetch():
    pubmed = PubMed(cache=True)

    # Mock successful fetch
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.text = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article><ArticleTitle>Test</ArticleTitle></Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    pubmed._session.get = Mock(return_value=mock_response)

    pubmed.fetch(["12345"])

    assert "12345" in pubmed._cache


# Task 3: cache returns cached articles
def test_cache_returns_cached_articles_no_api_call():
    pubmed = PubMed(cache=True)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.text = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article><ArticleTitle>Test</ArticleTitle></Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    pubmed._session.get = Mock(return_value=mock_response)

    # First fetch - API call
    pubmed.fetch(["12345"])
    assert pubmed._session.get.call_count == 1

    # Second fetch - no API call
    articles = pubmed.fetch(["12345"])
    assert pubmed._session.get.call_count == 1  # Still 1
    assert articles[0].pmid == "12345"


# Task 4: partial cache hit
def test_cache_fetches_only_missing_ids():
    pubmed = PubMed(cache=True)

    # First response for ID 12345
    response1 = Mock()
    response1.status_code = 200
    response1.raise_for_status = Mock()
    response1.text = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article><ArticleTitle>Article 1</ArticleTitle></Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """

    # Second response for ID 67890 only
    response2 = Mock()
    response2.status_code = 200
    response2.raise_for_status = Mock()
    response2.text = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>67890</PMID>
                <Article><ArticleTitle>Article 2</ArticleTitle></Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """

    pubmed._session.get = Mock(side_effect=[response1, response2])

    # First fetch
    pubmed.fetch(["12345"])

    # Second fetch with mixed IDs - should only fetch 67890
    articles = pubmed.fetch(["12345", "67890"])

    assert len(articles) == 2
    # Check that second call only requested 67890
    call_args = pubmed._session.get.call_args_list[1]
    assert "67890" in call_args[1]["params"]["id"]
    assert "12345" not in call_args[1]["params"]["id"]


# Task 5: TTL
def test_cache_ttl_default():
    pubmed = PubMed(cache=True)
    assert pubmed.cache_ttl == 3600  # 1 hour default


def test_cache_ttl_custom():
    pubmed = PubMed(cache=True, cache_ttl=60)
    assert pubmed.cache_ttl == 60


@patch("pypubmed.client.time.time")
def test_cache_expires_after_ttl(mock_time):
    pubmed = PubMed(cache=True, cache_ttl=60)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.text = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article><ArticleTitle>Test</ArticleTitle></Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    pubmed._session.get = Mock(return_value=mock_response)

    # First fetch at t=0
    mock_time.return_value = 0
    pubmed.fetch(["12345"])
    assert pubmed._session.get.call_count == 1

    # Second fetch at t=30 (within TTL) - cache hit
    mock_time.return_value = 30
    pubmed.fetch(["12345"])
    assert pubmed._session.get.call_count == 1

    # Third fetch at t=61 (after TTL) - cache miss
    mock_time.return_value = 61
    pubmed.fetch(["12345"])
    assert pubmed._session.get.call_count == 2


# Task 6: clear_cache
def test_clear_cache():
    pubmed = PubMed(cache=True)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.text = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article><ArticleTitle>Test</ArticleTitle></Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    pubmed._session.get = Mock(return_value=mock_response)

    pubmed.fetch(["12345"])
    assert "12345" in pubmed._cache

    pubmed.clear_cache()
    assert len(pubmed._cache) == 0
