from pypubmed import PubMed


def test_search_returns_ids():
    pubmed = PubMed()
    result = pubmed.search("cancer")
    assert len(result.ids) > 0


def test_search_returns_total_count():
    pubmed = PubMed()
    result = pubmed.search("cancer", max_results=5)
    assert result.count > 1000


def test_search_respects_max_results():
    pubmed = PubMed()
    result = pubmed.search("cancer", max_results=5)
    assert len(result.ids) == 5


def test_search_filters_by_date():
    pubmed = PubMed()
    result = pubmed.search("cancer", min_date="2024/06/01", max_date="2024/06/30")
    articles = pubmed.fetch(result.ids[:5])
    for article in articles:
        assert article.publication_date.year == 2024
        assert article.publication_date.month == 6


def test_search_and_fetch_returns_articles():
    pubmed = PubMed()
    articles = pubmed.search_and_fetch("CRISPR", max_results=3)
    assert len(articles) == 3
    assert all(a.pmid for a in articles)
