import pytest

from pypubmed import PubMed


PMID = "39344136"


def test_fetch_empty_ids_raises():
    pubmed = PubMed()
    with pytest.raises(ValueError):
        pubmed.fetch([])


from unittest.mock import Mock


def test_article_without_abstract():
    """Article without abstract should have empty string."""
    pubmed = PubMed()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.text = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article><ArticleTitle>Test Title</ArticleTitle></Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    pubmed._session.get = Mock(return_value=mock_response)

    articles = pubmed.fetch(["12345"])
    assert articles[0].abstract == ""


def test_article_without_doi():
    """Article without DOI should have None."""
    pubmed = PubMed()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.text = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article><ArticleTitle>Test Title</ArticleTitle></Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    pubmed._session.get = Mock(return_value=mock_response)

    articles = pubmed.fetch(["12345"])
    assert articles[0].doi is None


def test_article_without_publication_date():
    """Article without publication date should have None."""
    pubmed = PubMed()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.text = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>12345</PMID>
                <Article><ArticleTitle>Test Title</ArticleTitle></Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    pubmed._session.get = Mock(return_value=mock_response)

    articles = pubmed.fetch(["12345"])
    assert articles[0].publication_date is None


def test_fetch_malformed_xml_raises():
    """Malformed XML should raise an error."""
    from defusedxml.ElementTree import ParseError
    pubmed = PubMed()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.text = "<invalid xml"
    pubmed._session.get = Mock(return_value=mock_response)

    with pytest.raises(ParseError):
        pubmed.fetch(["12345"])


def test_fetch_chunks_large_batches():
    """Should split >200 IDs into chunks."""

    pubmed = PubMed()

    # Create mock response
    def make_response(ids):
        xml = "<PubmedArticleSet>"
        for id in ids.split(","):
            xml += f"""<PubmedArticle><MedlineCitation>
                <PMID>{id}</PMID>
                <Article><ArticleTitle>Test</ArticleTitle></Article>
            </MedlineCitation></PubmedArticle>"""
        xml += "</PubmedArticleSet>"
        mock = Mock()
        mock.status_code = 200
        mock.raise_for_status = Mock()
        mock.text = xml
        return mock

    # Mock to track calls and return appropriate responses
    call_count = [0]
    def mock_get(url, params, timeout):
        call_count[0] += 1
        return make_response(params["id"])

    pubmed._session.get = mock_get

    # Fetch 250 IDs (should be 2 chunks: 200 + 50)
    ids = [str(i) for i in range(250)]
    articles = pubmed.fetch(ids)

    assert len(articles) == 250
    assert call_count[0] == 2  # 2 API calls


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
