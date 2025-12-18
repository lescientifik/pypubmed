import pytest
from pypubmed import PubMed


PMID = "39344136"


@pytest.fixture(scope="module")
def articles():
    pubmed = PubMed()
    return pubmed.search_and_fetch("cancer", max_results=5)


@pytest.fixture(scope="module")
def article():
    pubmed = PubMed()
    return pubmed.fetch([PMID])[0]


def test_fetch_returns_one_article():
    pubmed = PubMed()
    articles = pubmed.fetch([PMID])
    assert len(articles) == 1


def test_article_has_correct_pmid(article):
    assert article.pmid == PMID


def test_article_has_title(article):
    assert article.title


def test_article_has_abstract(article):
    assert article.abstract


def test_article_has_authors(article):
    assert len(article.authors) > 0


def test_article_has_doi(article):
    assert article.doi.startswith("10.")


def test_article_has_url(article):
    assert article.url == f"https://pubmed.ncbi.nlm.nih.gov/{PMID}/"


def test_article_has_publication_date(article):
    # publication_date = electronic date (may be None for print-only articles)
    if article.publication_date:
        assert 1900 < article.publication_date.year < 2100
        assert 1 <= article.publication_date.month <= 12
        assert 1 <= article.publication_date.day <= 31


def test_article_has_journal_date(article):
    # journal_date = print journal issue date
    assert 1900 < article.journal_date.year < 2100
    assert 1 <= article.journal_date.month <= 12
    assert 1 <= article.journal_date.day <= 31


def test_article_has_journal(article):
    assert isinstance(article.journal, str)
    assert len(article.journal) > 3


@pytest.mark.parametrize("index", range(5))
def test_mesh_terms_is_list(articles, index):
    assert isinstance(articles[index].mesh_terms, list)


@pytest.mark.parametrize("index", range(5))
def test_mesh_terms_contains_valid_text(articles, index):
    mesh_terms = articles[index].mesh_terms
    if mesh_terms:
        assert any(c.isalnum() for c in mesh_terms[0])


@pytest.mark.parametrize("index", range(5))
def test_keywords_is_list(articles, index):
    assert isinstance(articles[index].keywords, list)


@pytest.mark.parametrize("index", range(5))
def test_keywords_contains_valid_text(articles, index):
    keywords = articles[index].keywords
    if keywords:
        assert any(c.isalnum() for c in keywords[0])
