from pypubmed import PubMed


def test_search_returns_article_ids():
    pubmed = PubMed()
    result = pubmed.search("cancer")
    assert len(result.ids) > 0
