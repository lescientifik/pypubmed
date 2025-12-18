from pypubmed import PubMed


PMID = "39344136"


def test_fetch_returns_one_article():
    pubmed = PubMed()
    articles = pubmed.fetch([PMID])
    assert len(articles) == 1


def test_article_has_correct_pmid():
    pubmed = PubMed()
    article = pubmed.fetch([PMID])[0]
    assert article.pmid == PMID


def test_article_has_title():
    pubmed = PubMed()
    article = pubmed.fetch([PMID])[0]
    assert article.title


def test_article_has_abstract():
    pubmed = PubMed()
    article = pubmed.fetch([PMID])[0]
    assert article.abstract


def test_article_has_authors():
    pubmed = PubMed()
    article = pubmed.fetch([PMID])[0]
    assert len(article.authors) > 0


def test_article_has_doi():
    pubmed = PubMed()
    article = pubmed.fetch([PMID])[0]
    assert article.doi.startswith("10.")


def test_article_has_url():
    pubmed = PubMed()
    article = pubmed.fetch([PMID])[0]
    assert article.url == f"https://pubmed.ncbi.nlm.nih.gov/{PMID}/"
