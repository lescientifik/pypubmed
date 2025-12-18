from pypubmed import PubMed, Article


def test_fetch_returns_articles():
    pubmed = PubMed()
    articles = pubmed.fetch(["39344136"])

    assert len(articles) == 1
    article = articles[0]
    assert isinstance(article, Article)
    assert article.pmid == "39344136"
    assert article.title
    assert article.abstract
    assert isinstance(article.authors, list)


def test_article_has_doi():
    pubmed = PubMed()
    articles = pubmed.fetch(["39344136"])
    article = articles[0]
    assert article.doi
    assert article.doi.startswith("10.")
