from pypubmed import PubMed


def test_search_returns_article_ids():
    pubmed = PubMed()
    result = pubmed.search("cancer")
    assert len(result.ids) > 0


def test_search_returns_total_count():
    pubmed = PubMed()
    result = pubmed.search("cancer", max_results=5)
    assert len(result.ids) == 5
    assert result.count > 1000  # "cancer" has millions of results
