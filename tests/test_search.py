import pytest

from pypubmed import PubMed


def test_search_invalid_max_results_raises():
    pubmed = PubMed()
    with pytest.raises(ValueError):
        pubmed.search("cancer", max_results=0)


def test_search_negative_max_results_raises():
    pubmed = PubMed()
    with pytest.raises(ValueError):
        pubmed.search("cancer", max_results=-1)


def test_search_returns_ids(search_result):
    assert len(search_result.ids) > 0


def test_search_returns_total_count(search_result):
    assert search_result.count > 1000


def test_search_respects_max_results(search_result):
    assert len(search_result.ids) == 5


def test_search_filters_by_date(articles_from_date_search):
    for article in articles_from_date_search:
        assert article.publication_date.year == 2024
        assert article.publication_date.month == 6


def test_search_and_fetch_returns_articles(search_and_fetch_result):
    assert len(search_and_fetch_result) == 3
    assert all(a.pmid for a in search_and_fetch_result)
