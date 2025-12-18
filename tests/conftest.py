import pytest
from pypubmed import PubMed


@pytest.fixture(scope="session")
def pubmed():
    return PubMed()


@pytest.fixture(scope="session")
def article(pubmed):
    """Single article for basic field tests."""
    return pubmed.fetch(["39344136"])[0]


@pytest.fixture(scope="session")
def articles(pubmed):
    """Multiple articles for parametrized tests."""
    return pubmed.search_and_fetch("cancer", max_results=5)


@pytest.fixture(scope="session")
def search_result(pubmed):
    """Search result for search tests."""
    return pubmed.search("cancer", max_results=5)


@pytest.fixture(scope="session")
def search_result_with_date(pubmed):
    """Search result with date filter."""
    return pubmed.search("cancer", min_date="2024/06/01", max_date="2024/06/30")


@pytest.fixture(scope="session")
def articles_from_date_search(pubmed, search_result_with_date):
    """Articles fetched from date-filtered search."""
    return pubmed.fetch(search_result_with_date.ids[:5])


@pytest.fixture(scope="session")
def search_and_fetch_result(pubmed):
    """Result from search_and_fetch for combined tests."""
    return pubmed.search_and_fetch("CRISPR", max_results=3)
